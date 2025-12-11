<?php
if (!defined('ABSPATH')) exit;

class ESGT_Export {
  /**
   * Build a clean printable HTML document from title + content
   * @param string $title
   * @param string $content HTML content (TinyMCE)
   * @param array  $options ['inline_images' => bool]
   */
  public static function build_html($title, $content, $options = []){
    $inline = !empty($options['inline_images']);
    $safe_title = wp_strip_all_tags($title ?: 'Proposal');
    // Allow rich content but filter dangerous tags
    $safe_content = wp_kses_post($content ?: '');

    // Normalize <img> tags
    if ($inline) {
      // Inline embed images as data URIs for Word reliability
      $safe_content = preg_replace_callback('/<img\b[^>]*>/i', function($m){
        $tag = $m[0];
        if (!preg_match('/src=(\"|\')([^\"\']+)(\1)/i', $tag, $ms)) return $tag;
        $src = html_entity_decode($ms[2]);
        if (strpos($src, 'data:') === 0) return $tag; // already embedded
        if (!preg_match('#^https?://#i', $src)) {
          $src = trailingslashit(home_url()) . ltrim($src, '/');
        }
        $res = wp_remote_get($src, ['timeout' => 15]);
        if (is_wp_error($res) || wp_remote_retrieve_response_code($res) !== 200) return $tag;
        $body = wp_remote_retrieve_body($res);
        if (!$body) return $tag;
        $mime = wp_remote_retrieve_header($res, 'content-type');
        if (!$mime) {
          $path = parse_url($src, PHP_URL_PATH);
          $ext = strtolower(pathinfo($path, PATHINFO_EXTENSION));
          $map = [
            'jpg' => 'image/jpeg', 'jpeg' => 'image/jpeg', 'png' => 'image/png', 'gif' => 'image/gif', 'webp' => 'image/webp', 'bmp' => 'image/bmp', 'svg' => 'image/svg+xml'
          ];
          $mime = isset($map[$ext]) ? $map[$ext] : 'image/jpeg';
        }
        // Convert WEBP to PNG for Word compatibility
        if ($mime === 'image/webp') {
          if (function_exists('imagecreatefromstring')) {
            $im = @imagecreatefromstring($body);
            if ($im) {
              ob_start();
              imagepng($im); // re-encode as PNG
              $pngData = ob_get_clean();
              imagedestroy($im);
              if ($pngData) {
                $body = $pngData;
                $mime = 'image/png';
              }
            }
          }
        }
        $data = 'data:' . $mime . ';base64,' . base64_encode($body);
        // replace src
        $tag = preg_replace('/src=(\"|\')[^\"\']+(\1)/i', 'src="' . esc_attr($data) . '"', $tag);
        // remove attributes that confuse Word
        $tag = preg_replace('/\s(?:srcset|sizes|loading|decoding)=(\"|\')[^\"\']*(\1)/i', '', $tag);
        return $tag;
      }, $safe_content);
    } else {
      // Convert relative image src to absolute URLs
      $safe_content = preg_replace_callback('/<img[^>]+src=[\"\']([^\"\']+)[\"\'][^>]*>/i', function($m){
        $src = $m[1];
        if (strpos($src, 'http://') === 0 || strpos($src, 'https://') === 0) return $m[0];
        $abs = esc_url_raw( (trailingslashit(home_url()) . ltrim($src,'/')) );
        return str_replace($src, $abs, $m[0]);
      }, $safe_content);
    }

    ob_start(); ?>
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title><?php echo esc_html($safe_title); ?></title>
  <style>
    body{ font-family: Georgia, 'Times New Roman', serif; color:#000; background:#fff; }
    .container{ max-width:800px; margin:40px auto; padding:0 20px; line-height:1.6; }
    h1,h2,h3,h4{ margin:1.2em 0 .6em; }
    img{ max-width:100%; height:auto; }
    p{ margin:.6em 0; }
  </style>
</head>
<body>
  <div class="container">
    <h1><?php echo esc_html($safe_title); ?></h1>
  <?php echo apply_filters('the_content', $safe_content); ?>
  </div>
</body>
</html>
<?php
    return ob_get_clean();
  }
}
