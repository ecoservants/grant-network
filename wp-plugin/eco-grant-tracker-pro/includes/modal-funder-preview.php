<?php
/**
 * EcoServants® Grant Tracker Pro
 * Modal Funder Preview Template (Simplified + Direct IRS Search Link + Working Close)
 */

if (!defined('ABSPATH')) exit;

global $wpdb;
$id = isset($_POST['id']) ? intval($_POST['id']) : 0;
if (!$id) wp_send_json_error(['message' => 'Invalid ID']);

try {
  $dsn = sprintf(
    'mysql:host=%s;port=%s;dbname=%s;charset=utf8mb4',
    get_option('esgt_db')['host'],
    get_option('esgt_db')['port'],
    get_option('esgt_db')['name']
  );
  $pdo = new PDO($dsn, get_option('esgt_db')['user'], get_option('esgt_db')['pass']);
  $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

  $stmt = $pdo->prepare('SELECT * FROM grants WHERE id = ? LIMIT 1');
  $stmt->execute([$id]);
  $grant = $stmt->fetch(PDO::FETCH_ASSOC);
} catch (Exception $e) {
  wp_send_json_error(['message' => 'Database error: ' . $e->getMessage()]);
}

if (!$grant) wp_send_json_error(['message' => 'Grant not found.']);

ob_start(); ?>
<style>
  .esgt-modal-body {
    font-family: 'Poppins', system-ui, sans-serif;
    line-height: 1.6;
    padding: 1.5rem;
    color: #1b2432;
    position: relative;
  }
  .esgt-modal-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #243b7e;
    border-bottom: 3px solid #243b7e;
    padding-bottom: .4rem;
    margin-bottom: 1rem;
  }
  .esgt-section { margin-bottom: 1.25rem; }
  .esgt-section h3 {
    font-size: 1.1rem;
    color: #243b7e;
    border-left: 4px solid #243b7e;
    padding-left: .5rem;
    margin-bottom: .5rem;
  }
  .esgt-section p { margin: .25rem 0; }
  .esgt-financials {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: .5rem 1rem;
    background: #f5f7fc;
    border-radius: .5rem;
    padding: 1rem;
  }
  .esgt-financials p { margin: .2rem 0; font-weight: 500; }
  .esgt-actions { text-align: right; margin-top: 1rem; }
  .esgt-btn {
    display: inline-block;
    background: #243b7e;
    color: #fff !important;
    padding: .6rem 1.2rem;
    border-radius: .4rem;
    text-decoration: none;
    font-weight: 600;
    letter-spacing: 0.3px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    transition: all .25s ease;
  }
  .esgt-btn:hover {
    background: #1b2d65;
    color: #fff !important;
    transform: translateY(-1px);
  }
  .esgt-separator {
    border-bottom: 1px dashed #ccd2e3;
    margin: 1rem 0;
  }
  .esgt-modal-body a { color: #243b7e; }

  .esgt-modal-close {
    position: absolute;
    top: 12px;
    right: 12px;
    background: transparent;
    border: none;
    font-size: 1.4rem;
    color: #243b7e;
    width: 34px;
    height: 34px;
    line-height: 34px;
    text-align: center;
    border-radius: 50%;
    cursor: pointer;
    transition: all .25s ease;
  }
  .esgt-modal-close:hover {
    background: #243b7e;
    color: #fff;
    transform: rotate(90deg);
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  }

  @media (max-width: 600px) {
    .esgt-modal-body { padding: 1rem; font-size: .95rem; }
    .esgt-financials { grid-template-columns: 1fr; }
    .esgt-actions { text-align: center; }
  }
</style>

<div class="esgt-modal-body">
  <button class="esgt-modal-close" type="button" data-close>&times;</button>

  <h2 class="esgt-modal-title"><?php echo esc_html($grant['funder']); ?></h2>

  <div class="esgt-section">
    <p><strong>Type:</strong> <?php echo esc_html($grant['funder_type']); ?></p>
  </div>

  <div class="esgt-separator"></div>

  <div class="esgt-section">
    <h3>Contact Information</h3>
    <p><strong>Address:</strong><br><?php echo nl2br(esc_html($grant['address'])); ?></p>

    <?php if (!empty($grant['website'])): ?>
      <p><strong>Website:</strong>
        <a href="<?php echo esc_url($grant['website']); ?>" target="_blank" rel="noopener">
          <?php echo esc_html($grant['website']); ?>
        </a>
      </p>
    <?php endif; ?>

    <?php if (!empty($grant['phone'])): ?>
      <p><strong>Phone:</strong> <?php echo esc_html($grant['phone']); ?></p>
    <?php endif; ?>

    <?php if (!empty($grant['ein'])): ?>
      <p><strong>EIN:</strong> <?php echo esc_html($grant['ein']); ?></p>
      <div style="margin-top:.75rem">
        <a href="https://apps.irs.gov/app/eos/#/search/ein/<?php echo esc_attr($grant['ein']); ?>" 
           target="_blank" 
           rel="noopener" 
           class="esgt-btn">
           Open IRS 990 Search in New Tab
        </a>
      </div>
    <?php endif; ?>
  </div>

  <div class="esgt-separator"></div>

  <div class="esgt-section">
    <h3>Financial Overview</h3>
    <div class="esgt-financials">
      <p><strong>Total Assets:</strong><br>$<?php echo number_format($grant['total_assets']); ?></p>
      <p><strong>Total Giving:</strong><br>$<?php echo number_format($grant['total_giving']); ?></p>
      <p><strong>Average Grant:</strong><br>$<?php echo number_format($grant['avg_grant_amount']); ?></p>
      <p><strong>Median Grant:</strong><br>$<?php echo number_format($grant['median_grant_amount']); ?></p>
    </div>
  </div>

  <?php if (!empty($grant['notes'])): ?>
    <div class="esgt-separator"></div>
    <div class="esgt-section">
      <h3>Notes</h3>
      <p><?php echo nl2br(esc_html($grant['notes'])); ?></p>
    </div>
  <?php endif; ?>

  <div class="esgt-actions">
    <?php if (!empty($grant['website'])): ?>
      <a href="<?php echo esc_url($grant['website']); ?>" target="_blank" class="esgt-btn" rel="noopener">
        Apply / Visit Website
      </a>
    <?php endif; ?>
  </div>
</div>

<?php
$html = ob_get_clean();
wp_send_json_success(['html' => $html]);
?>
