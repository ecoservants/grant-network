(function($){

  /* ========================================================
     (LEGACY CLEANUP) – make sure any leftover inline rows are gone
  ======================================================== */
  $(function(){ $('.esgt-edit-row').remove(); });

  /* ========================================================
     MODAL PREVIEW
  ======================================================== */
  function openModal(html){
    const $m = $('#esgt-modal');
    $m.removeClass('is-open').attr('aria-hidden','true');
    $m.find('.esgt-modal-content').html(html);
    void $m[0].offsetWidth;
    $m.attr('aria-hidden','false').addClass('is-open');
    $('body').addClass('esgt-modal-open');
  }
  function closeModal(){
    const $m = $('#esgt-modal');
    $m.removeClass('is-open').attr('aria-hidden','true');
    $m.find('.esgt-modal-content').empty();
    $('body').removeClass('esgt-modal-open');
  }

  $(document).on('click','.esgt-preview',function(e){
    e.preventDefault();
    const id = $(this).data('id');
    $.post(ESGT.ajax_url,{action:'esgt_preview_grant',id:id,nonce:ESGT.nonce},function(resp){
      if(resp && resp.success && resp.data?.html) openModal(resp.data.html);
      else alert('Preview not available.');
    });
  });
  $(document).on('click','#esgt-modal [data-close],#esgt-modal .esgt-modal-backdrop',closeModal);
  $(document).on('keydown',e=>{ if(e.key==='Escape') closeModal(); });

  /* ========================================================
     SEARCH + FILTER
  ======================================================== */
  $(document).on('input','.esgt-search',function(){
    const q = $(this).val().toLowerCase().trim();
    let count = 0;
    $('.esgt-grant-card').each(function(){
      const show = !q || $(this).text().toLowerCase().includes(q);
      $(this).toggle(show);
      if(show) count++;
    });
    const toolbar = $('.esgt-toolbar');
    toolbar.find('.esgt-results').remove();
    toolbar.append(`<span class="esgt-results">${count} result${count!==1?'s':''}</span>`);
  });

  $(document).on('change','.esgt-status-filter',function(){
    const val = $(this).val().toLowerCase();
    let count = 0;
    $('.esgt-grant-card').each(function(){
      const s = $(this).find('.esgt-status').text().toLowerCase();
      const show = !val || s.includes(val);
      $(this).toggle(show);
      if(show) count++;
    });
    const toolbar = $('.esgt-toolbar');
    toolbar.find('.esgt-results').remove();
    toolbar.append(`<span class="esgt-results">${count} result${count!==1?'s':''}</span>`);
  });

  /* ========================================================
     CARD FADE ANIMATION
  ======================================================== */
  const cards = document.querySelectorAll('.esgt-grant-card');
  cards.forEach((c,i)=>c.style.setProperty('--card-index',i));

})(jQuery);
