<?php
/*
Plugin Name: EcoServants Grant Tracker Pro
Plugin URI: https://ecoservantsproject.org
Description: Advanced external-database grant tracker with proposal editor, funder preview, paginated grid, and live IRS 990 data proxy.
Version: 1.4
Author: EcoServants Project
Author URI: https://ecoservantsproject.org
License: GPL2
*/

if (!defined('ABSPATH')) exit;

define('ESGT_PRO_PATH', plugin_dir_path(__FILE__));
define('ESGT_PRO_URL', plugin_dir_url(__FILE__));

require_once ESGT_PRO_PATH . 'includes/class-esgt-db.php';
require_once ESGT_PRO_PATH . 'includes/class-esgt-proposal.php';

/* ===============================================
   Admin Menu – Database Settings
=============================================== */
add_action('admin_menu', function(){
  add_options_page('Grant Tracker DB', 'Grant Tracker DB', 'manage_options', 'esgt-db-settings', 'esgt_db_settings_page');
});

add_action('admin_init', function(){
  register_setting('esgt_db', 'esgt_db');
});

function esgt_encrypt($data){
  if(empty($data)) return '';
  $key = defined('AUTH_KEY') ? AUTH_KEY : 'ecoservants';
  $iv = substr(hash('sha256', $key), 0, 16);
  return base64_encode(openssl_encrypt($data, 'AES-256-CBC', $key, 0, $iv));
}
function esgt_decrypt($data){
  if(empty($data)) return '';
  $key = defined('AUTH_KEY') ? AUTH_KEY : 'ecoservants';
  $iv = substr(hash('sha256', $key), 0, 16);
  return openssl_decrypt(base64_decode($data), 'AES-256-CBC', $key, 0, $iv);
}

function esgt_db_settings_page(){
  $opts = get_option('esgt_db', []); ?>
  <div class="wrap">
    <h1>External Database Settings</h1>
    <form method="post" action="options.php">
      <?php settings_fields('esgt_db'); ?>
      <table class="form-table">
        <tr><th>Host</th><td><input type="text" name="esgt_db[host]" value="<?php echo esc_attr($opts['host'] ?? ''); ?>"></td></tr>
        <tr><th>Port</th><td><input type="text" name="esgt_db[port]" value="<?php echo esc_attr($opts['port'] ?? '3306'); ?>"></td></tr>
        <tr><th>Database</th><td><input type="text" name="esgt_db[name]" value="<?php echo esc_attr($opts['name'] ?? ''); ?>"></td></tr>
        <tr><th>User</th><td><input type="text" name="esgt_db[user]" value="<?php echo esc_attr($opts['user'] ?? ''); ?>"></td></tr>
        <tr><th>Password</th><td><input type="password" name="esgt_db[pass]" value="<?php echo esc_attr(esgt_decrypt($opts['pass'] ?? '')); ?>"></td></tr>
      </table>
      <?php submit_button('Save Settings'); ?>
    </form>
  </div>
  <?php
}

/* ===============================================
   Enqueue Scripts & Styles
=============================================== */
add_action('admin_enqueue_scripts', function(){
  wp_enqueue_style('esgt-admin', ESGT_PRO_URL . 'assets/admin-modern.css');
});

add_action('wp_enqueue_scripts', function(){
  wp_enqueue_script('esgt-front', ESGT_PRO_URL . 'assets/front.js', ['jquery'], null, true);
  wp_localize_script('esgt-front', 'ESGT', [
    'ajax_url' => admin_url('admin-ajax.php'),
    'nonce' => wp_create_nonce('esgt_nonce'),
    'statuses' => ['Researching','Planned','In Progress','Submitted','Awarded','Declined']
  ]);
  wp_enqueue_style('esgt-front-style', ESGT_PRO_URL . 'assets/admin-modern.css');
  // Removed TinyMCE/editor assets as proposal writing functionality has been deprecated
});

/* ===============================================
   Unified Shortcode [grant_tracker_pro]
   — Pagination + Proposal Editor + Modal Preview
=============================================== */
add_shortcode('grant_tracker_pro', function(){
  $db = new ESGT_DB();

  $page = isset($_GET['pg']) ? max(1, intval($_GET['pg'])) : 1;
  $limit = 18;
  $offset = ($page - 1) * $limit;

  // Paginated query
  $pdo = new PDO(
    sprintf('mysql:host=%s;port=%s;dbname=%s;charset=utf8mb4',
      get_option('esgt_db')['host'],
      get_option('esgt_db')['port'],
      get_option('esgt_db')['name']
    ),
    get_option('esgt_db')['user'],
    get_option('esgt_db')['pass']
  );
  $stmt = $pdo->prepare("SELECT * FROM grants ORDER BY deadline ASC LIMIT :limit OFFSET :offset");
  $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
  $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
  $stmt->execute();
  $grants = $stmt->fetchAll(PDO::FETCH_ASSOC);

  $total = $pdo->query('SELECT COUNT(*) FROM grants')->fetchColumn();
  $totalPages = ceil($total / $limit);

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
    <?php foreach($grants as $g): ?>
      <div class="esgt-grant-card" data-id="<?php echo esc_attr($g['id']); ?>" data-proposal="<?php echo esc_attr($g['proposal'] ?? ''); ?>">
        <h3>
          <a href="#" class="esgt-funder-title" data-funder-url="<?php echo esc_url($g['website']); ?>">
            <?php echo esc_html($g['funder']); ?>
          </a>
        </h3>
        <p>Type: <?php echo esc_html($g['funder_type']); ?></p>
        <p><strong>Total Giving:</strong> $<?php echo number_format((float)$g['total_giving']); ?></p>
        <p><strong>Average Grant:</strong> $<?php echo number_format((float)$g['avg_grant_amount']); ?></p>
        <p><strong>Assets:</strong> $<?php echo number_format((float)$g['total_assets']); ?></p>
        <p><strong>Status:</strong> 
          <span class="esgt-status"><?php echo esc_html($g['status']); ?></span>
        </p>
        <a href="#" class="esgt-btn esgt-preview" data-id="<?php echo esc_attr($g['id']); ?>">Preview</a>
        <?php if (is_user_logged_in()): ?>
          <a href="#" class="esgt-btn esgt-write-proposal" data-id="<?php echo esc_attr($g['id']); ?>" data-funder="<?php echo esc_attr($g['funder']); ?>">Write Proposal</a>
        <?php endif; ?>
        <?php if (!empty($g['website'])): ?>
          <a href="<?php echo esc_url($g['website']); ?>" target="_blank" class="esgt-btn">Visit Website</a>
        <?php endif; ?>
      </div>
    <?php endforeach; ?>
  </div>

  <?php if ($totalPages > 1): ?>
    <div class="esgt-pagination">
      <?php if ($page > 1): ?>
        <a href="?pg=<?php echo $page - 1; ?>" class="esgt-btn">Previous</a>
      <?php endif; ?>
      <span>Page <?php echo $page; ?> of <?php echo $totalPages; ?></span>
      <?php if ($page < $totalPages): ?>
        <a href="?pg=<?php echo $page + 1; ?>" class="esgt-btn">Next</a>
      <?php endif; ?>
    </div>
  <?php endif; ?>

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
   AJAX: Update Grant (Save Proposal Editor)
=============================================== */
add_action('wp_ajax_esgt_update_grant', function(){
  check_ajax_referer('esgt_nonce', 'nonce');
  $db = new ESGT_DB();

  $id = intval($_POST['id'] ?? 0);
  $data = [
    'status' => sanitize_text_field($_POST['status'] ?? ''),
    'next_task' => sanitize_text_field($_POST['next_task'] ?? ''),
    'next_due' => sanitize_text_field($_POST['next_due'] ?? ''),
    'notes' => sanitize_textarea_field($_POST['notes'] ?? ''),
    'proposal' => wp_kses_post($_POST['proposal'] ?? '')
  ];

  $ok = $db->update_grant($id, $data);
  if ($ok) wp_send_json_success(['message' => 'Grant updated']);
  else wp_send_json_error(['message' => 'Database update failed']);
});

/* =======================================================
   Modal Preview (includes/modal-funder-preview.php)
======================================================= */
add_action('wp_ajax_esgt_preview_grant', function(){
  check_ajax_referer('esgt_nonce', 'nonce');
  require_once ESGT_PRO_PATH . 'includes/modal-funder-preview.php';
  exit;
});
add_action('wp_ajax_nopriv_esgt_preview_grant', function(){
  require_once ESGT_PRO_PATH . 'includes/modal-funder-preview.php';
  exit;
});

/* =======================================================
   IRS 990 Proxy – Server-Side Fetch (CORS Safe)
======================================================= */
add_action('wp_ajax_esgt_get_irs990', 'esgt_get_irs990');
add_action('wp_ajax_nopriv_esgt_get_irs990', 'esgt_get_irs990');

function esgt_get_irs990() {
  check_ajax_referer('esgt_nonce', 'nonce');
  $ein = sanitize_text_field($_GET['ein'] ?? '');
  if (empty($ein)) wp_send_json_error(['message' => 'Missing EIN.']);

  $url = "https://projects.propublica.org/nonprofits/api/v2/organizations/{$ein}.json";
  $response = wp_remote_get($url, ['timeout' => 10]);
  if (is_wp_error($response)) wp_send_json_error(['message' => 'Failed to fetch IRS data.']);
  $body = wp_remote_retrieve_body($response);
  if (!$body) wp_send_json_error(['message' => 'Empty IRS response.']);

  $data = json_decode($body, true);
  wp_send_json_success($data);
}

/* Proposal editor removed in v1.5: TinyMCE modal and related scripts have been deleted */

/* Proposal draft AJAX endpoints removed in v1.5 */
/* =======================================================
   REST API Endpoint: /wp-json/esgt/v1/grants
   Returns normalized grant data from external DB
======================================================= */
add_action('rest_api_init', function() {
  register_rest_route('esgt/v1', '/grants', [
    'methods'  => 'GET',
    'callback' => 'esgt_rest_list_grants',
    'permission_callback' => '__return_true'
  ]);
});

function esgt_rest_list_grants($request) {
  $opts = get_option('esgt_db', []);
  try {
    $pdo = new PDO(
      sprintf('mysql:host=%s;port=%s;dbname=%s;charset=utf8mb4',
        $opts['host'], $opts['port'], $opts['name']
      ),
      $opts['user'], $opts['pass']
    );
  } catch (Exception $e) {
    return new WP_Error('db_connect_error', 'Database connection failed: ' . $e->getMessage(), ['status' => 500]);
  }

  /* ----------------------------
     Parameters
  ---------------------------- */
  $limit  = intval($request->get_param('limit') ?: 50);
  $page   = intval($request->get_param('page') ?: 1);
  $offset = ($page - 1) * $limit;

  $state  = sanitize_text_field($request->get_param('state') ?: '');
  $funder = sanitize_text_field($request->get_param('funder') ?: '');
  $status = sanitize_text_field($request->get_param('status') ?: '');
  $search = sanitize_text_field($request->get_param('search') ?: '');
  $format = sanitize_text_field($request->get_param('format') ?: 'json');

  /* ----------------------------
     Query Builder
  ---------------------------- */
  $sql = "SELECT id, title, funder, funder_type, deadline, amount, status, website 
          FROM grants WHERE 1=1";
  $params = [];

  if ($state) {
    $sql .= " AND state = :state";
    $params[':state'] = $state;
  }
  if ($funder) {
    $sql .= " AND funder LIKE :funder";
    $params[':funder'] = '%' . $funder . '%';
  }
  if ($status) {
    $sql .= " AND status = :status";
    $params[':status'] = $status;
  }
  if ($search) {
    $sql .= " AND (title LIKE :search OR funder LIKE :search)";
    $params[':search'] = '%' . $search . '%';
  }

  $sql .= " ORDER BY deadline ASC LIMIT :limit OFFSET :offset";

  $stmt = $pdo->prepare($sql);
  foreach ($params as $key => $val) {
    $stmt->bindValue($key, $val);
  }
  $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
  $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
  $stmt->execute();
  $data = $stmt->fetchAll(PDO::FETCH_ASSOC);

  /* ----------------------------
     Total Count
  ---------------------------- */
  $countStmt = $pdo->prepare("SELECT COUNT(*) FROM grants");
  $countStmt->execute();
  $total = $countStmt->fetchColumn();

  /* ----------------------------
     CSV Export (format=csv)
  ---------------------------- */
  if ($format === 'csv') {
    header('Content-Type: text/csv');
    header('Content-Disposition: attachment; filename="grants.csv"');

    $output = fopen('php://output', 'w');
    if (!empty($data)) {
      fputcsv($output, array_keys($data[0]));
      foreach ($data as $row) {
        fputcsv($output, $row);
      }
    }
    fclose($output);
    exit;
  }

  /* ----------------------------
     JSON Response
  ---------------------------- */
  return rest_ensure_response([
    'page'  => $page,
    'limit' => $limit,
    'total' => intval($total),
    'count' => count($data),
    'data'  => $data
  ]);
}
