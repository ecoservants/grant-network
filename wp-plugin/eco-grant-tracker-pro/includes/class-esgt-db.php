<?php
if (!defined('ABSPATH')) exit;

class ESGT_DB {
  private $pdo;

  public function __construct() {
    $cfg = get_option('esgt_db', []);
    $dsn = "mysql:host={$cfg['host']};port={$cfg['port']};dbname={$cfg['name']};charset=utf8mb4";
    try {
      $this->pdo = new PDO($dsn, $cfg['user'], $cfg['pass'], [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
      ]);
    } catch (Exception $e) {
      wp_die('DB Connection failed: ' . $e->getMessage());
    }
  }

  /* ===============================================
     CRUD Methods
  =============================================== */
  public function get_grants() {
    $stmt = $this->pdo->query("SELECT * FROM grants ORDER BY deadline ASC");
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
  }

  public function get_grant($id) {
    $stmt = $this->pdo->prepare("SELECT * FROM grants WHERE id=? LIMIT 1");
    $stmt->execute([$id]);
    return $stmt->fetch(PDO::FETCH_ASSOC);
  }

  public function update_grant($id, $data) {
    $stmt = $this->pdo->prepare("
      UPDATE grants 
      SET status=?, next_task=?, next_due=?, notes=?, proposal=? 
      WHERE id=?");
    return $stmt->execute([
      $data['status'], 
      $data['next_task'], 
      $data['next_due'], 
      $data['notes'], 
      $data['proposal'], 
      $id
    ]);
  }

  /* ===============================================
     CSV Import
  =============================================== */
  public function import_csv($filepath) {
    if (!file_exists($filepath)) return false;
    $handle = fopen($filepath, 'r');
    if (!$handle) return false;

    $header = fgetcsv($handle);
    $inserted = 0;
    $sql = "INSERT INTO grants 
      (title, funder, funder_type, num_saved_opps, total_amount_requesting, total_assets, total_giving, avg_grant_amount, median_grant_amount, ein, address, phone, website, contacts, notes, status)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
    $stmt = $this->pdo->prepare($sql);

    while (($row = fgetcsv($handle)) !== false) {
      $data = array_combine($header, $row);
      if (!$data) continue;
      $stmt->execute([
        $data['Funder Name'] ?? '', $data['Funder Name'] ?? '', $data['Funder Type'] ?? '',
        $data['Number of Saved Opportunities'] ?? 0, $data['Total Amount Requesting'] ?? 0,
        $data['Total Assets'] ?? 0, $data['Total Giving'] ?? 0, $data['Average Grant Amount'] ?? 0,
        $data['Median Grant Amount'] ?? 0, $data['EIN'] ?? '', $data['Address'] ?? '',
        $data['Phone Number'] ?? '', $data['Website'] ?? '', $data['Number of Points of Contact'] ?? 0,
        $data['Funder Notes'] ?? '', 'Imported'
      ]);
      $inserted++;
    }

    fclose($handle);
    return $inserted;
  }
}

/* ===============================================
   Shortcode [grant_tracker_pro] — Enhanced Grid
=============================================== */
add_shortcode('grant_tracker_pro', function($atts){
  $db = new ESGT_DB();
  $grants = $db->get_grants();
  ob_start(); ?>
  <div class="esgt-toolbar">
    <input type="search" class="esgt-search" placeholder="Search funders or keywords...">
    <select class="esgt-status-filter">
      <option value="">All Statuses</option>
      <option value="Researching">Researching</option>
      <option value="Planned">Planned</option>
      <option value="In Progress">In Progress</option>
      <option value="Submitted">Submitted</option>
      <option value="Awarded">Awarded</option>
      <option value="Declined">Declined</option>
    </select>
  </div>

  <div class="esgt-grant-grid">
    <?php foreach ($grants as $g): ?>
      <div class="esgt-grant-card" data-id="<?php echo esc_attr($g['id']); ?>">
        <h3>
          <a href="#" class="esgt-funder-title" data-funder-url="<?php echo esc_url($g['website']); ?>">
            <?php echo esc_html($g['funder']); ?>
          </a>
        </h3>
        <p class="esgt-desc">Type: <?php echo esc_html($g['funder_type']); ?></p>
        <p><strong>Total Giving:</strong> $<?php echo number_format((float)$g['total_giving']); ?></p>
        <p><strong>Average Grant:</strong> $<?php echo number_format((float)$g['avg_grant_amount']); ?></p>
        <p><strong>Assets:</strong> $<?php echo number_format((float)$g['total_assets']); ?></p>
        <p><strong>Status:</strong> 
          <span class="esgt-status" data-status="<?php echo esc_attr($g['status']); ?>">
            <?php echo esc_html($g['status']); ?>
          </span>
        </p>
        <a href="#" class="esgt-btn esgt-preview" data-id="<?php echo esc_attr($g['id']); ?>">Preview Grant</a>
        <?php if (!empty($g['website'])): ?>
          <a href="<?php echo esc_url($g['website']); ?>" target="_blank" class="esgt-btn">Visit Website</a>
        <?php endif; ?>
      </div>
    <?php endforeach; ?>
  </div>

  <div id="esgt-modal" class="esgt-modal" aria-hidden="true">
    <div class="esgt-modal-backdrop" data-close></div>
    <div class="esgt-modal-dialog" tabindex="-1">
      <button class="esgt-modal-close" data-close>&times;</button>
      <div class="esgt-modal-content"></div>
    </div>
  </div>
  <?php
  return ob_get_clean();
});

/* ===============================================
   Admin Import Tool — Tools > Import Funders CSV
=============================================== */
add_action('admin_menu', function(){
  add_management_page('Import Funders CSV', 'Import Funders CSV', 'manage_options', 'esgt-import-csv', function(){
    if (!current_user_can('manage_options')) return;
    echo '<div class="wrap"><h1>Import Funder Data (CSV)</h1>';
    if (isset($_FILES['esgt_csv']) && is_uploaded_file($_FILES['esgt_csv']['tmp_name'])) {
      $db = new ESGT_DB();
      $count = $db->import_csv($_FILES['esgt_csv']['tmp_name']);
      echo '<div class="updated"><p>Imported ' . intval($count) . ' funder records successfully.</p></div>';
    }
    echo '<form method="post" enctype="multipart/form-data">';
    echo '<input type="file" name="esgt_csv" accept=".csv" required> ';
    submit_button('Import CSV');
    echo '</form></div>';
  });
});

/* ===============================================
   IRS 990 Data Proxy — Prefill Fallback Only
=============================================== */
add_action('wp_ajax_esgt_get_irs990', function () {
  check_ajax_referer('esgt_nonce', 'nonce');
  $ein = preg_replace('/[^0-9]/', '', $_GET['ein'] ?? '');
  if (!$ein) wp_send_json_error(['message' => 'Missing EIN']);

  $data = [
    'organization' => ['city' => '', 'state' => ''],
    'filings_with_data' => [[
      'total_revenue' => 0,
      'total_expenses' => 0,
      'total_assets' => 0,
      'tax_prd_yr' => date('Y'),
      'form_type' => '990',
      'label' => 'IRS Search Portal',
      'prefill_link' => "https://apps.irs.gov/app/eos/#/search/ein/$ein"
    ]]
  ];

  wp_send_json_success($data);
});

/* ===============================================
   AJAX: Update Grant (Status, Notes, Proposal)
=============================================== */
add_action('wp_ajax_esgt_update_grant', function() {
  check_ajax_referer('esgt_nonce', 'nonce');

  $id = intval($_POST['id'] ?? 0);
  if (!$id) wp_send_json_error(['message' => 'Missing grant ID']);

  $data = [
    'status'    => sanitize_text_field($_POST['status'] ?? ''),
    'next_task' => sanitize_text_field($_POST['next_task'] ?? ''),
    'next_due'  => sanitize_text_field($_POST['next_due'] ?? ''),
    'notes'     => sanitize_textarea_field($_POST['notes'] ?? ''),
    'proposal'  => wp_kses_post($_POST['proposal'] ?? '')
  ];

  try {
    $db = new ESGT_DB();
    $ok = $db->update_grant($id, $data);
    if ($ok) wp_send_json_success(['message' => 'Grant updated']);
    else wp_send_json_error(['message' => 'Database update failed']);
  } catch (Exception $e) {
    wp_send_json_error(['message' => $e->getMessage()]);
  }
});
?>
