<?php
if (!defined('ABSPATH')) exit;

/**
 * ESGT Proposal: custom post type and AJAX endpoints
 */
class ESGT_Proposal {
  public static function init() {
    add_action('init', [__CLASS__, 'register_cpt']);

    // Front-end assets and UI
    add_action('wp_enqueue_scripts', [__CLASS__, 'enqueue_front_assets']);
    add_action('wp_footer', [__CLASS__, 'render_editor_modal']);
    add_action('wp_footer', [__CLASS__, 'render_link_bar']);

    // AJAX endpoints (logged-in)
    add_action('wp_ajax_esgt_save_proposal', [__CLASS__, 'ajax_save_proposal']);
    add_action('wp_ajax_esgt_get_user_proposal', [__CLASS__, 'ajax_get_user_proposal']);
    add_action('wp_ajax_esgt_export_proposal', [__CLASS__, 'ajax_export_proposal']);
    add_action('wp_ajax_esgt_export_proposal_doc', [__CLASS__, 'ajax_export_proposal_doc']);
    add_action('wp_ajax_esgt_get_latest_proposal', [__CLASS__, 'ajax_get_latest_proposal']);
    add_action('wp_ajax_esgt_get_user_proposals', [__CLASS__, 'ajax_get_user_proposals']);
  }

  public static function register_cpt() {
    $labels = [
      'name' => __('Proposals', 'esgt'),
      'singular_name' => __('Proposal', 'esgt'),
    ];

    register_post_type('esgt_proposal', [
      'labels' => $labels,
      'public' => true, // allow viewing permalink when logged in
      'show_ui' => true,
      'show_in_menu' => true,
      'show_in_rest' => true,
      'exclude_from_search' => true,
      'has_archive' => false,
      'publicly_queryable' => true,
      'supports' => ['title','editor','author','revisions','thumbnail'],
      'rewrite' => ['slug' => 'proposal', 'with_front' => false],
      'capability_type' => 'post',
      'map_meta_cap' => true,
    ]);
  }

  public static function enqueue_front_assets() {
    if (!is_user_logged_in()) return; // Only for logged-in users

    // Ensure editor + media assets are available on the front end
    if (function_exists('wp_enqueue_editor')) {
      wp_enqueue_editor();
    } else {
      wp_enqueue_script('editor');
      wp_enqueue_style('editor-buttons');
    }
    wp_enqueue_media();
  }

  public static function render_editor_modal() {
    if (!is_user_logged_in()) return;
    // Hidden modal present on page so TinyMCE can initialize properly
    ?>
  <div id="esgt-proposal-modal" class="esgt-modal" aria-hidden="true">
      <div class="esgt-modal-backdrop" data-close></div>
      <div class="esgt-modal-dialog" tabindex="-1" style="max-width: 900px; width: 95vw;">
        <button class="esgt-modal-close" type="button" data-close>&times;</button>
        <div class="esgt-modal-content" style="padding:16px;">
          <h2 style="margin-top:0;">Write Proposal</h2>
          <div class="esgt-proposal-form">
            <input type="hidden" id="esgt_proposal_grant_id" value="">
            <div style="margin-bottom:10px;">
              <label for="esgt_proposal_title" style="display:block; font-weight:600; margin-bottom:4px;">Title</label>
              <input type="text" id="esgt_proposal_title" class="regular-text" style="width:100%; padding:8px;" placeholder="Proposal title">
            </div>
            <div style="margin-bottom:10px;">
              <?php
                $settings = [
                  'media_buttons' => true,
                  'textarea_rows' => 14,
                  'teeny' => false,
                  'quicktags' => true,
                  'tinymce' => [
                    'toolbar1' => 'formatselect,bold,italic,underline,bullist,numlist,blockquote,alignleft,aligncenter,alignright,link,unlink,wp_more,undo,redo',
                    'toolbar2' => 'fontsizeselect,forecolor,backcolor,outdent,indent,table,removeformat,charmap,wp_help'
                  ],
                ];
                // Render editor with empty content; we'll programmatically set later
                wp_editor('', 'esgt_proposal_editor', $settings);
              ?>
            </div>
            <div style="display:flex; gap:8px; justify-content:flex-end; margin-top:8px;">
              <button class="esgt-btn" id="esgt_save_proposal_btn" type="button">Save Draft</button>
              <button class="esgt-btn" id="esgt_export_proposal_btn" type="button" title="Export as Word (.doc)">Export Word</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <style>
      /* Modal visibility control: hidden unless .is-open */
      #esgt-proposal-modal[aria-hidden="true"] { display:none; }
      #esgt-proposal-modal.esgt-modal.is-open { display:block; }
      #esgt-proposal-modal .wp-editor-container { border:1px solid #ccd2e3; border-radius:6px; }
  /* Proposal banner readability improvements */
  #esgt-proposal-items { align-items:flex-start !important; }
  #esgt-proposal-items .esgt-proposal-chip { background:#fff; border:1px solid #b8c3d9; border-radius:8px; padding:10px 12px; display:flex; flex-direction:column; width:300px; height:170px; box-shadow:0 2px 4px rgba(0,0,0,.05); font-size:13px; line-height:1.45; position:relative; overflow:hidden; }
  #esgt-proposal-items .esgt-proposal-head { display:flex; align-items:center; gap:8px; margin-bottom:6px; }
  #esgt-proposal-items .esgt-proposal-head a { color:#163d86; font-weight:600; text-decoration:none; display:inline-block; max-width:calc(100% - 84px); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  #esgt-proposal-items .esgt-proposal-head a:hover { text-decoration:underline; }
  #esgt-proposal-items .esgt-proposal-head .spacer { flex:1 1 auto; }
  #esgt-proposal-items .esgt-proposal-funder { width:100%; border-top:1px solid #e3e8f2; padding-top:6px; margin-top:4px; overflow:hidden; }
  #esgt-proposal-items .esgt-proposal-funder table { width:100%; border-collapse:collapse; }
  #esgt-proposal-items .esgt-proposal-funder table tr { border-bottom:1px dotted #dde3ef; }
  #esgt-proposal-items .esgt-proposal-funder table tr:last-child { border-bottom:none; }
  #esgt-proposal-items .esgt-proposal-funder table th { text-align:left; font-weight:600; padding:2px 4px; width:46%; color:#2f466d; font-size:12px; }
  #esgt-proposal-items .esgt-proposal-funder table td { padding:2px 4px; font-size:12px; color:#1a2330; }
  #esgt-proposal-items .esgt-proposal-chip .esgt-proposal-item-edit { font-size:12px; }
  #esgt-proposal-items .esgt-btn.esgt-btn-sm { padding:4px 8px; font-size:12px; line-height:1.2; border-radius:6px; }
  /* Compact on very small widths */
  @media (max-width:640px){ #esgt-proposal-items .esgt-proposal-chip { min-width:100%; } }
    </style>
    <?php
  }

  public static function render_link_bar() {
    if (!is_user_logged_in()) return;
    ?>
    <style>
      /* Minimize button and mini launcher styles */
      #esgt-proposal-link-bar .esgt-proposals-minimize{background:transparent;border:0;color:#4a5a7a;font-size:18px;line-height:1;width:28px;height:28px;border-radius:6px;cursor:pointer}
      #esgt-proposal-link-bar .esgt-proposals-minimize:hover{background:#e9eefb}
      #esgt-proposal-mini{position:fixed;left:16px;bottom:12px;z-index:100000;display:none;background:#243b7e;color:#fff;border:1px solid #1f2f5f;border-radius:999px;padding:10px 14px;font-weight:600;box-shadow:0 2px 10px rgba(0,0,0,.12);cursor:pointer}
      #esgt-proposal-mini:hover{background:#1f326d}
    </style>
    <div id="esgt-proposal-link-bar" style="position:fixed; left:16px; right:16px; bottom:12px; display:none; z-index:100000;">
      <div style="background:#f5f7fc; border:1px solid #ccd2e3; border-radius:8px; padding:10px 12px; display:flex; align-items:center; gap:12px; box-shadow:0 2px 10px rgba(0,0,0,.06);">
        <strong style="color:#243b7e; white-space:nowrap;">Your proposals:</strong>
        <div id="esgt-proposal-items" style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
          <!-- items injected here -->
        </div>
        <span style="flex:1"></span>
        <div id="esgt-proposal-pager" style="display:flex; gap:6px; align-items:center;">
          <button type="button" class="esgt-btn" id="esgt-proposals-prev" style="padding:.3rem .6rem;">‹</button>
          <span id="esgt-proposals-page" style="color:#243b7e; opacity:.8; font-weight:600;">1</span>
          <button type="button" class="esgt-btn" id="esgt-proposals-next" style="padding:.3rem .6rem;">›</button>
        </div>
        <button type="button" id="esgt-proposals-minimize" class="esgt-proposals-minimize" aria-label="Minimize proposals bar" title="Hide this bar">×</button>
      </div>
    </div>
    <button id="esgt-proposal-mini" type="button" aria-label="Open Proposal Editor" title="Open Proposal Editor">Open Proposal Editor</button>
    <script>
      (function($){
        // ---- Banner visibility helpers ----
        function setBannerState(state){
          try{ localStorage.setItem('esgtProposalBannerState', state); }catch(e){}
        }
        function getBannerState(){
          try{ return localStorage.getItem('esgtProposalBannerState') || 'expanded'; }catch(e){ return 'expanded'; }
        }
        function showBanner(){ $('#esgt-proposal-link-bar').show(); $('#esgt-proposal-mini').hide(); setBannerState('expanded'); }
        function hideBanner(){ $('#esgt-proposal-link-bar').hide(); $('#esgt-proposal-mini').show(); setBannerState('minimized'); }

        function getEditorContent(){
          const ed = window.tinymce && tinymce.get('esgt_proposal_editor');
          if (ed && !ed.isHidden()) return ed.getContent();
          return $('#esgt_proposal_editor').val();
        }
        function setEditorContent(html){
          const ed = window.tinymce && tinymce.get('esgt_proposal_editor');
          if (ed) { ed.setContent(html || ''); ed.undoManager && ed.undoManager.clear(); }
          $('#esgt_proposal_editor').val(html || '');
        }

        $(document).on('click','.esgt-write-proposal',function(e){
          e.preventDefault();
          if(!ESGT || !ESGT.nonce){ alert('Not authorized.'); return; }
          const grantId = $(this).closest('.esgt-grant-card').data('id') || $(this).data('id');
          const funderName = $(this).closest('.esgt-grant-card').find('h3').text().trim() || $(this).data('funder') || 'Untitled Proposal';
          $('#esgt_proposal_grant_id').val(grantId);
          $('#esgt_proposal_title').val(funderName + ' – Proposal');
          // Fetch existing proposal if any
          $.post(ESGT.ajax_url,{action:'esgt_get_user_proposal',nonce:ESGT.nonce,grant_id:grantId},function(resp){
            if(resp && resp.success && resp.data){
              if(resp.data.title) $('#esgt_proposal_title').val(resp.data.title);
              if(resp.data.content) setEditorContent(resp.data.content);
            } else {
              setEditorContent('');
            }
            // Open modal
            const $m = $('#esgt-proposal-modal');
            $m.attr('aria-hidden','false').addClass('is-open');
            $('body').addClass('esgt-modal-open');
          });
        });

        $(document).on('click','#esgt-proposal-modal [data-close], #esgt-proposal-modal .esgt-modal-backdrop',function(){
          const $m = $('#esgt-proposal-modal');
          $m.removeClass('is-open').attr('aria-hidden','true');
          $('body').removeClass('esgt-modal-open');
        });

        $(document).on('click','#esgt_save_proposal_btn',function(){
          const grantId = $('#esgt_proposal_grant_id').val();
          const title = $('#esgt_proposal_title').val();
          const content = getEditorContent();
          $(this).prop('disabled',true).text('Saving...');
          $.post(ESGT.ajax_url,{action:'esgt_save_proposal',nonce:ESGT.nonce,grant_id:grantId,title:title,content:content},function(resp){
            $('#esgt_save_proposal_btn').prop('disabled',false).text('Save Draft');
            if(resp && resp.success && resp.data){
              // Update link bar
              $('#esgt-proposal-link').attr('href', resp.data.url);
              $('#esgt-proposal-title').text('“' + (resp.data.title||'') + '”');
              $('#esgt-edit-proposal-link').off('click').on('click', function(e){ e.preventDefault(); $('#esgt-proposal-modal').addClass('is-open').attr('aria-hidden','false'); $('body').addClass('esgt-modal-open'); });
              if (getBannerState()==='minimized') { $('#esgt-proposal-mini').fadeIn(150); } else { $('#esgt-proposal-link-bar').fadeIn(150); $('#esgt-proposal-mini').hide(); }
            } else {
              alert((resp && resp.data && resp.data.message) || 'Failed to save.');
            }
          });
        });

        // When a funder preview opens, fetch link (if user has one) and show bar
        $(document).on('click','.esgt-preview',function(){
          const id = $(this).data('id');
          $.post(ESGT.ajax_url,{action:'esgt_get_user_proposal',nonce:ESGT.nonce,grant_id:id},function(resp){
            if(resp && resp.success && resp.data && resp.data.url){
              // Render as single-item list when previewing, include funder summary
              const items = [{title: resp.data.title, url: resp.data.url, grant_id: id, funder: resp.data.funder || null}];
              renderProposalItems(items, 1, 1, 1);
              if (getBannerState()==='minimized') { $('#esgt-proposal-mini').fadeIn(150); } else { $('#esgt-proposal-link-bar').fadeIn(150); $('#esgt-proposal-mini').hide(); }
            }
          });
        });

        // Helper to render list of proposals
        function renderProposalItems(items, page, perPage, total){
          const $wrap = $('#esgt-proposal-items').empty();
          items.forEach(function(it){
            const $chip = $('<div class="esgt-proposal-chip" role="group" aria-label="Saved proposal">');
            const $head = $('<div class="esgt-proposal-head">');
            const titleText = (it.title||'Untitled');
            const $link = $('<a href="#" class="esgt-proposal-item-open" aria-label="Open funder preview for '+titleText.replace(/\"/g,'')+'">').data('grant-id', it.grant_id||'').text(titleText);
            const $spacer = $('<span class="spacer"></span>');
            const $edit = $('<button type="button" class="esgt-btn esgt-btn-sm esgt-proposal-item-edit" aria-label="Edit proposal '+titleText.replace(/\"/g,'')+'">').data('grant-id', it.grant_id||'').text('Edit');
            $head.append($link).append($spacer).append($edit);
            $chip.append($head);
            if (it.funder){
              const fmtMoney = v => (v==null?'-':'$'+Number(v).toLocaleString());
              const $summary = $('<div class="esgt-proposal-funder">');
              const $table = $('<table aria-label="Funder summary">');
              const rows = [
                ['Funder', it.funder.funder||'Unknown'],
                ['Type', it.funder.funder_type||'-'],
                ['Total Giving', fmtMoney(it.funder.total_giving)],
                ['Avg Grant', fmtMoney(it.funder.avg_grant_amount)],
                ['Assets', fmtMoney(it.funder.total_assets)]
              ];
              if (it.funder.status) rows.push(['Status', it.funder.status]);
              rows.forEach(r=>{ $table.append($('<tr>').append($('<th>').text(r[0])).append($('<td>').text(r[1]))); });
              $summary.append($table);
              $chip.append($summary);
            }
            $wrap.append($chip);
          });
          const pages = Math.max(1, Math.ceil(total / perPage));
          $('#esgt-proposals-page').text(page + ' / ' + pages);
          $('#esgt-proposals-prev').prop('disabled', page<=1);
          $('#esgt-proposals-next').prop('disabled', page>=pages);
        }

        // Persist banner proposals with responsive pagination (desktop:4, mobile:1)
        $(function(){
          if (!$('.esgt-grant-grid').length) return;
          let page = 1; let perPage = getPerPage(); let total = 0; let lastWidth = window.innerWidth;

          function getPerPage(){ return window.innerWidth < 640 ? 1 : 4; }

            // Reload if breakpoint changes (e.g., rotate / resize)
          $(window).on('resize', function(){
            const w = window.innerWidth;
            const current = getPerPage();
            if (current !== perPage) {
              perPage = current;
              page = 1; // reset to first page when layout changes
              loadPage(page);
            }
            lastWidth = w;
          });

          function loadPage(p){
            $.post(ESGT.ajax_url,{action:'esgt_get_user_proposals',nonce:ESGT.nonce,page:p,per_page:perPage},function(resp){
              if(resp && resp.success && resp.data && resp.data.items && resp.data.items.length){
                total = resp.data.total || resp.data.items.length;
                page = p;
                renderProposalItems(resp.data.items, page, perPage, total);
                // Apply minimized/expanded state
                if (getBannerState()==='minimized') { $('#esgt-proposal-link-bar').hide(); $('#esgt-proposal-mini').show(); } else { $('#esgt-proposal-link-bar').show(); $('#esgt-proposal-mini').hide(); }
              } else if (p === 1) {
                $('#esgt-proposal-link-bar').hide();
                $('#esgt-proposal-mini').hide();
              }
            });
          }
          loadPage(page);
          $(document).on('click','#esgt-proposals-prev', function(){ if (page>1) loadPage(page-1); });
          $(document).on('click','#esgt-proposals-next', function(){ const pages = Math.max(1, Math.ceil(total/perPage)); if (page<pages) loadPage(page+1); });
          $(document).on('click','.esgt-proposal-item-edit', function(e){
            e.preventDefault();
            const grantId = $(this).data('grant-id');
            if (grantId){
              $.post(ESGT.ajax_url,{action:'esgt_get_user_proposal',nonce:ESGT.nonce,grant_id:grantId},function(r){
                $('#esgt_proposal_grant_id').val(grantId);
                if(r && r.success && r.data){
                  if(r.data.title) $('#esgt_proposal_title').val(r.data.title);
                  if(r.data.content){ const ed = window.tinymce && tinymce.get('esgt_proposal_editor'); if (ed) ed.setContent(r.data.content); else $('#esgt_proposal_editor').val(r.data.content); }
                }
                $('#esgt-proposal-modal').addClass('is-open').attr('aria-hidden','false'); $('body').addClass('esgt-modal-open');
              });
            } else {
              $('#esgt-proposal-modal').addClass('is-open').attr('aria-hidden','false'); $('body').addClass('esgt-modal-open');
            }
          });

          // Open funder preview when clicking proposal title in banner
          $(document).on('click','.esgt-proposal-item-open', function(e){
            e.preventDefault();
            const grantId = $(this).data('grant-id');
            if (!grantId) return;
            $.post(ESGT.ajax_url,{action:'esgt_preview_grant',id:grantId,nonce:ESGT.nonce},function(resp){
              if(resp && resp.success && resp.data?.html){
                const $m = $('#esgt-modal');
                $m.find('.esgt-modal-content').html(resp.data.html);
                $m.attr('aria-hidden','false').addClass('is-open');
                $('body').addClass('esgt-modal-open');
              }
            });
          });

          // Minimize / restore handlers
          $(document).on('click', '#esgt-proposals-minimize', function(){ hideBanner(); });
          $(document).on('click', '#esgt-proposal-mini', function(){ showBanner(); });
        });

        // Export Word (.doc) via admin-ajax streaming response
        $(document).on('click','#esgt_export_proposal_btn',function(){
          const $btn = $(this);
          $btn.prop('disabled',true).text('Preparing...');
          const title = ($('#esgt_proposal_title').val() || 'Proposal').trim();
          const content = (function(){
            const ed = window.tinymce && tinymce.get('esgt_proposal_editor');
            if (ed && !ed.isHidden()) return ed.getContent();
            return $('#esgt_proposal_editor').val();
          })();
          if(!content || !content.trim()){
            alert('No content to export.');
            $btn.prop('disabled',false).text('Export Word');
            return;
          }
          const form = document.createElement('form');
          form.method = 'POST';
          form.action = ESGT.ajax_url;
          form.style.display = 'none';
          const params = {
            action: 'esgt_export_proposal_doc',
            nonce: ESGT.nonce,
            title: title,
            content: content
          };
          Object.keys(params).forEach(k=>{
            const input = document.createElement('input');
            input.type = 'hidden'; input.name = k; input.value = params[k];
            form.appendChild(input);
          });
          document.body.appendChild(form);
          form.submit();
          setTimeout(()=>{ $btn.prop('disabled',false).text('Export Word'); form.remove(); }, 1500);
        });
      })(jQuery);
    </script>
    <?php
  }

  /**
   * Return latest proposal for current user (for persistent banner)
   */
  public static function ajax_get_latest_proposal() {
    check_ajax_referer('esgt_nonce', 'nonce');
    if (!is_user_logged_in()) wp_send_json_success(null);
    $user_id = get_current_user_id();
    $posts = get_posts([
      'post_type' => 'esgt_proposal',
      'author' => $user_id,
      'posts_per_page' => 1,
      'post_status' => ['private','draft','publish'],
      'orderby' => 'modified',
      'order' => 'DESC'
    ]);
    if (!$posts) wp_send_json_success(null);
    $p = $posts[0];
    $grant_id = get_post_meta($p->ID, 'esgt_grant_id', true);
    wp_send_json_success([
      'id' => $p->ID,
      'title' => $p->post_title,
      'url' => get_permalink($p),
      'grant_id' => $grant_id ? intval($grant_id) : null,
    ]);
  }

  /**
   * Return paginated proposals for current user
   * POST: page, per_page
   */
  public static function ajax_get_user_proposals() {
    check_ajax_referer('esgt_nonce', 'nonce');
    if (!is_user_logged_in()) wp_send_json_success(['items'=>[], 'total'=>0, 'page'=>1, 'per_page'=>3]);
    $user_id = get_current_user_id();
    $page = max(1, intval($_POST['page'] ?? 1));
    $per_page = max(1, min(10, intval($_POST['per_page'] ?? 3)));

    $args = [
      'post_type' => 'esgt_proposal',
      'author' => $user_id,
      'posts_per_page' => $per_page,
      'post_status' => ['private','draft','publish'],
      'orderby' => 'modified',
      'order' => 'DESC',
      'offset' => ($page - 1) * $per_page,
      'fields' => 'all'
    ];
    $q = new WP_Query($args);
    $items = [];
    if ($q->have_posts()) {
      foreach ($q->posts as $p) {
        $grant_id = get_post_meta($p->ID, 'esgt_grant_id', true);
        $funder_summary = null;
        if ($grant_id && class_exists('ESGT_DB')) {
          try {
            $db = new ESGT_DB();
            $grant = $db->get_grant(intval($grant_id));
            if ($grant) {
              $funder_summary = [
                'funder' => sanitize_text_field($grant['funder'] ?? ''),
                'funder_type' => sanitize_text_field($grant['funder_type'] ?? ''),
                'total_giving' => isset($grant['total_giving']) ? floatval($grant['total_giving']) : null,
                'avg_grant_amount' => isset($grant['avg_grant_amount']) ? floatval($grant['avg_grant_amount']) : null,
                'total_assets' => isset($grant['total_assets']) ? floatval($grant['total_assets']) : null,
                'status' => sanitize_text_field($grant['status'] ?? ''),
              ];
            }
          } catch (Exception $e) {
            $funder_summary = null; // Fail silently
          }
        }
        $items[] = [
          'id' => $p->ID,
          'title' => $p->post_title,
          'url' => get_permalink($p),
          'grant_id' => $grant_id ? intval($grant_id) : null,
          'modified' => get_post_modified_time('c', true, $p)
          ,'funder' => $funder_summary
        ];
      }
    }
    // Total count
    $count_q = new WP_Query([
      'post_type' => 'esgt_proposal',
      'author' => $user_id,
      'posts_per_page' => 1,
      'post_status' => ['private','draft','publish'],
      'fields' => 'ids'
    ]);
    $total = $count_q->found_posts;
    wp_send_json_success(['items' => $items, 'total' => intval($total), 'page' => $page, 'per_page' => $per_page]);
  }

  public static function ajax_get_user_proposal() {
    check_ajax_referer('esgt_nonce', 'nonce');
    if (!is_user_logged_in()) wp_send_json_error(['message' => 'Not logged in'], 403);
    $user_id = get_current_user_id();
    $grant_id = intval($_POST['grant_id'] ?? 0);
    if (!$grant_id) wp_send_json_error(['message' => 'Missing grant id']);

    $existing = get_posts([
      'post_type' => 'esgt_proposal',
      'author' => $user_id,
      'posts_per_page' => 1,
      'post_status' => ['private','draft','publish'],
      'meta_query' => [[
        'key' => 'esgt_grant_id',
        'value' => $grant_id,
        'compare' => '='
      ]]
    ]);

    if ($existing) {
      $p = $existing[0];
      $funder_summary = null;
      if ($grant_id && class_exists('ESGT_DB')) {
        try {
          $db = new ESGT_DB();
          $grant = $db->get_grant(intval($grant_id));
          if ($grant) {
            $funder_summary = [
              'funder' => sanitize_text_field($grant['funder'] ?? ''),
              'funder_type' => sanitize_text_field($grant['funder_type'] ?? ''),
              'total_giving' => isset($grant['total_giving']) ? floatval($grant['total_giving']) : null,
              'avg_grant_amount' => isset($grant['avg_grant_amount']) ? floatval($grant['avg_grant_amount']) : null,
              'total_assets' => isset($grant['total_assets']) ? floatval($grant['total_assets']) : null,
              'status' => sanitize_text_field($grant['status'] ?? ''),
            ];
          }
        } catch (Exception $e) {
          $funder_summary = null;
        }
      }
      wp_send_json_success([
        'id' => $p->ID,
        'title' => $p->post_title,
        'url' => get_permalink($p),
        'content' => $p->post_content,
        'funder' => $funder_summary,
      ]);
    } else {
      wp_send_json_success(null);
    }
  }

  public static function ajax_save_proposal() {
    check_ajax_referer('esgt_nonce', 'nonce');
    if (!is_user_logged_in()) wp_send_json_error(['message' => 'Not logged in'], 403);
    $user_id = get_current_user_id();

    $grant_id = intval($_POST['grant_id'] ?? 0);
    $title = sanitize_text_field($_POST['title'] ?? 'Untitled Proposal');
    $content = wp_kses_post($_POST['content'] ?? '');

    if (!$grant_id) wp_send_json_error(['message' => 'Missing grant id']);

    // Find existing proposal by user + grant
    $existing = get_posts([
      'post_type' => 'esgt_proposal',
      'author' => $user_id,
      'posts_per_page' => 1,
      'post_status' => ['private','draft','publish'],
      'meta_query' => [[
        'key' => 'esgt_grant_id',
        'value' => $grant_id,
        'compare' => '='
      ]]
    ]);

    $postarr = [
      'post_title' => $title,
      'post_content' => $content,
      'post_type' => 'esgt_proposal',
      'post_status' => 'private',
      'post_author' => $user_id,
    ];

    if ($existing) {
      $postarr['ID'] = $existing[0]->ID;
      $post_id = wp_update_post($postarr, true);
    } else {
      $post_id = wp_insert_post($postarr, true);
      if (!is_wp_error($post_id)) {
        update_post_meta($post_id, 'esgt_grant_id', $grant_id);
      }
    }

    if (is_wp_error($post_id)) {
      wp_send_json_error(['message' => $post_id->get_error_message()]);
    }

    wp_send_json_success([
      'id' => $post_id,
      'url' => get_permalink($post_id),
      'title' => get_the_title($post_id),
    ]);
  }

  public static function ajax_export_proposal() {
    check_ajax_referer('esgt_nonce', 'nonce');
    if (!is_user_logged_in()) wp_send_json_error(['message' => 'Not logged in'], 403);
    $user_id = get_current_user_id();
    $grant_id = intval($_POST['grant_id'] ?? 0);
    if (!$grant_id) wp_send_json_error(['message' => 'Missing grant id']);

    $existing = get_posts([
      'post_type' => 'esgt_proposal',
      'author' => $user_id,
      'posts_per_page' => 1,
      'post_status' => ['private','draft','publish'],
      'meta_query' => [[
        'key' => 'esgt_grant_id',
        'value' => $grant_id,
        'compare' => '='
      ]]
    ]);

    if (!$existing) wp_send_json_error(['message' => 'No proposal found']);

    $p = $existing[0];
    if (!class_exists('ESGT_Export')) {
      require_once ESGT_PRO_PATH . 'includes/class-esgt-export.php';
    }
    $html = ESGT_Export::build_html(get_the_title($p), $p->post_content);
    wp_send_json_success(['html' => $html, 'length' => strlen($html)]);
  }

  public static function ajax_export_proposal_doc() {
    // Stream a Word-compatible .doc file built from current content (HTML inside)
    check_ajax_referer('esgt_nonce', 'nonce');
    if (!is_user_logged_in()) wp_die('Not authorized');
    $title = sanitize_text_field($_POST['title'] ?? 'Proposal');
    $content_raw = wp_kses_post($_POST['content'] ?? '');
    if (!class_exists('ESGT_Export')) {
      require_once ESGT_PRO_PATH . 'includes/class-esgt-export.php';
    }
    $html = ESGT_Export::build_html($title, $content_raw, ['inline_images' => true]);
    $filename = preg_replace('/[^a-zA-Z0-9_\-]/','_', $title) . '.doc';
    header('Content-Type: application/msword');
    header('Content-Disposition: attachment; filename="' . $filename . '"');
    header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
    echo $html; // Word can parse HTML in .doc container
    exit;
  }
}

ESGT_Proposal::init();
