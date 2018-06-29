(function($) {
  "use strict";
  $(document).ready(function() {
    var opts = {
      auto: {
        speed: 3500,
        pauseOnHover: true
      },
      fullScreen: false,
      swipe: false,
    };
    makeBSS('.bss-slides', opts);

    $('a.advanced-search-btn').click(function(e) {
      e.preventDefault();
      $('.woo-search-elements').toggleClass('active');
    });
    $('a.advanced-search-btn-procced').click(function(e) {
      e.preventDefault();
      $('#search-form').submit();
    });
    $('.top-search button').hover(function(e) {
      $('.advanced-search-btn').toggleClass('hover');
    })

    $("#id_category").on('change', function() {
      $("#id_products").prop('checked', true);
    });

    // $(".variables select").each(function() {
    //   if (!isMobile) {
    //     var sb = new SelectBox({
    //       selectbox: $(this)
    //     });
    //     void(sb);
    //   }
    // });
    // var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ? true : false;
    // if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    //   $(".variables select").css({
    //     'display': 'block'
    //   });
    // }

    $("#cart").hoverIntent({
      sensitivity: 3,
      interval: 60,
      over: function() {
        $('.cart-list', this).fadeIn(200);
        $('.cart-btn a.button', this).addClass('hovered');
      },
      timeout: 220,
      out: function() {
        $('.cart-list', this).fadeOut(100);
        $('.cart-btn a.button', this).removeClass('hovered');
      }
    });

    $(document).on('touchend click', '.menu-trigger', function(e) {
      $(".menu").toggleClass("responsive");
      e.preventDefault();
      return false;
    });
    $(".toggle-filter-button").on('click touch', function(e) {
      e.preventDefault();
      $(this).next('.filter-panel').toggleClass('visible');
      // var panel = $(this).next('.filter-panel');
      // if($(panel).hasClass("visible"))
      //   {
      //    $(panel).fadeOut(150, function() {
      //      $(panel).removeClass('visible');
      //   });
      //
      //   } else {
      //   $(panel).fadeIn(150, function() {
      //      $(panel).addClass('visible');
      //   });
      //   }
      return false;
    });

    $(".parallax-banner").pureparallax({
      overlayBackgroundColor: '#000',
      overlayOpacity: '0.45',
      timeout: 0
    });

    // $("#slider-range").slider({
    //   range: true,
    //   min: 0,
    //   max: 100,
    //   values: [0, 100],
    //   slide: function(event, ui) {
    //     event = event;
    //     $("#amount").val("rub" + ui.values[0] + " - rub" + ui.values[1]);
    //   }
    // });
    // $("#amount").val("" + $("#slider-range").slider("values", 0) + " - " + $("#slider-range").slider("values", 1));
    // $("#slider-range-alt").slider({
    //   range: true,
    //   min: 0,
    //   max: 500,
    //   values: [0, 500],
    //   slide: function(event, ui) {
    //     event = event;
    //     $("#amount").val("rub" + ui.values[0] + " - rub" + ui.values[1]);
    //   }
    // });
    // $("#amount").val("rub" + $("#slider-range").slider("values", 0) + " - rub" + $("#slider-range").slider("values", 1));

    $('#product-slider').royalSlider({
      autoScaleSlider: true,
      autoScaleSliderWidth: 560,
      autoHeight: true,
      loop: false,
      slidesSpacing: 0,
      imageScaleMode: 'none',
      imageAlignCenter: false,
      navigateByClick: false,
      numImagesToPreload: 2,
      arrowsNav: true,
      arrowsNavAutoHide: false,
      arrowsNavHideOnTouch: true,
      keyboardNavEnabled: true,
      fadeinLoadedSlide: true,
      controlNavigation: 'thumbnails',
      thumbs: {
        orientation: 'horizontal',
        firstMargin: false,
        appendSpan: true,
        autoCenter: false,
        spacing: 10,
        paddingTop: 10,
      }
    });
    var slider = $('#product-slider');
    var nav = slider.find('.rsThumbs');
    if (slider.length != 0) {
      if (slider.data('royalSlider').numSlides <= 1) {
        nav.hide();
      } else {
        nav.show();
      }
    }

    var thisrowfield;
    $('.qtyplus').click(function(e) {
      e.preventDefault();
      // console.log('plus');
      thisrowfield = $(this).prev('input');
      var currentVal = parseInt(thisrowfield.val());
      if (!isNaN(currentVal)) {
        thisrowfield.val(currentVal + 1);
      } else {
        thisrowfield.val(0);
      }
    });
    $(".qtyminus").click(function(e) {
      e.preventDefault();
      thisrowfield = $(this).next('input');
      var currentVal = parseInt(thisrowfield.val());
      if (!isNaN(currentVal) && currentVal > 0) {
        thisrowfield.val(currentVal - 1);
      } else {
        thisrowfield.val(0);
      }
    });
    var $tabsNav = $('.tabs-nav'),
      $tabsNavLis = $tabsNav.children('li');
    $tabsNav.each(function() {
      var $this = $(this);
      $this.next().children('.tab-content').stop(true, true).hide().first().show();
      $this.children('li').first().addClass('active').stop(true, true).show();
    });
    $tabsNavLis.on('click', function(e) {
      var $this = $(this);
      $this.siblings().removeClass('active').end().addClass('active');
      $this.parent().next().children('.tab-content').stop(true, true).hide().siblings($this.find('a').attr('href')).fadeIn();
      e.preventDefault();
    });
    // var $accor = $('.accordion');
    // $accor.each(function() {
    //   $(this).addClass('ui-accordion ui-widget ui-helper-reset');
    //   $(this).find('h3').addClass('ui-accordion-header ui-helper-reset ui-state-default ui-accordion-icons ui-corner-all');
    //   $(this).find('div').addClass('ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom');
    //   $(this).find("div").hide().first().show();
    //   $(this).find("h3").first().removeClass('ui-accordion-header-active ui-state-active ui-corner-top').addClass('ui-accordion-header-active ui-state-active ui-corner-top');
    //   $(this).find("span").first().addClass('ui-accordion-icon-active');
    // });
    // var $trigger = $accor.find('h3');
    // $trigger.on('click', function(e) {
    //   var location = $(this).parent();
    //   if ($(this).next().is(':hidden')) {
    //     var $triggerloc = $('h3', location);
    //     $triggerloc.removeClass('ui-accordion-header-active ui-state-active ui-corner-top').next().slideUp(300);
    //     $triggerloc.find('span').removeClass('ui-accordion-icon-active');
    //     $(this).find('span').addClass('ui-accordion-icon-active');
    //     $(this).addClass('ui-accordion-header-active ui-state-active ui-corner-top').next().slideDown(300);
    //   }
    //   e.preventDefault();
    // });
    // $(".toggle-container").hide();
    // $(".trigger").toggle(function() {
    //   $(this).addClass("active");
    // }, function() {
    //   $(this).removeClass("active");
    // });
    // $(".trigger").click(function() {
    //   $(this).next(".toggle-container").slideToggle();
    // });
    // $(".trigger.opened").toggle(function() {
    //   $(this).removeClass("active");
    // }, function() {
    //   $(this).addClass("active");
    // });
    // $(".trigger.opened").addClass("active").next(".toggle-container").show();
    // $('.counter').counterUp({
    //   delay: 10,
    //   time: 2000
    // });
    $("a.close").removeAttr("href").click(function() {
      $(this).parent().fadeOut(200);
    });
    // $(".tooltip.top").tipTip({
    //   defaultPosition: "top"
    // });
    // $(".tooltip.bottom").tipTip({
    //   defaultPosition: "bottom"
    // });
    // $(".tooltip.left").tipTip({
    //   defaultPosition: "left"
    // });
    // $(".tooltip.right").tipTip({
    //   defaultPosition: "right"
    // });
    $(document).ready(function() {
      $('body').magnificPopup({
        type: 'image',
        delegate: 'a.mfp-gallery',
        fixedContentPos: true,
        fixedBgPos: true,
        overflowY: 'auto',
        closeBtnInside: true,
        preloader: true,
        removalDelay: 0,
        mainClass: 'mfp-fade',
        gallery: {
          enabled: true
        },
        callbacks: {
          buildControls: function() {
            // this.contentContainer.append(this.arrowLeft.add(this.arrowRight));
          }
        }
      });
      $('.popup-with-zoom-anim').magnificPopup({
        type: 'inline',
        fixedContentPos: false,
        fixedBgPos: true,
        overflowY: 'auto',
        closeBtnInside: true,
        preloader: false,
        midClick: true,
        removalDelay: 300,
        mainClass: 'my-mfp-zoom-in'
      });
      $('.mfp-image').magnificPopup({
        type: 'image',
        closeOnContentClick: true,
        mainClass: 'mfp-fade',
        image: {
          verticalFit: true
        }
      });
      $('.popup-youtube, .popup-vimeo, .popup-gmaps').magnificPopup({
        disableOn: 700,
        type: 'iframe',
        mainClass: 'mfp-fade',
        removalDelay: 160,
        preloader: false,
        fixedContentPos: false
      });
    });

    $(window).load(function() {
      var $container = $('#portfolio-wrapper, #masonry-wrapper');
      $container.isotope({
        itemSelector: '.portfolio-item, .masonry-item',
        masonry: {
          horizontalOrder: true
        },
        filter: $('#filters a.selected').attr('data-filter')
      });
    });


    var pxShow = 600;
    var fadeInTime = 400;
    var fadeOutTime = 400;
    var scrollSpeed = 400;
    jQuery(window).scroll(function() {
      if (jQuery(window).scrollTop() >= pxShow) {
        jQuery("#topper").fadeIn(fadeInTime);
      } else {
        jQuery("#topper").fadeOut(fadeOutTime);
      }
    });
    jQuery('#topper a').click(function() {
      jQuery('html, body').animate({
        scrollTop: 0
      }, scrollSpeed);
      return false;
    });
    // function addLevelClass($parent, level) {
    //         $parent.addClass('parent-' + level);
    //         var $children = $parent.children('li');
    //         $children.addClass('child-' + level).data('level', level);
    //         $children.each(function() {
    //             var $sublist = $(this).children('ul');
    //             if ($sublist.length > 0) {
    //                 $(this).addClass('has-sublist');
    //                 addLevelClass($sublist, level + 1);
    //             }
    //         });
    //     }
    //     // addLevelClass($('#categories'), 1);
    //     $('#categories > li a').click(function(e) {
    //         if ($(this).parent().hasClass('has-sublist')) { e.preventDefault(); }
    //         if ($(this).attr('class') != 'active') {
    //             $(this).parent().siblings().find('ul').slideUp();
    //             $(this).next().slideToggle();
    //             if ($(this).parent().hasClass("has-sublist")) {
    //                 $(this).parent().siblings().find('a').removeClass('active');
    //                 $(this).addClass('active');
    //             } else { var curlvl = $(this).parent().data('level'); if (curlvl) { $('#categories li.child-' + curlvl + ' a').removeClass('active'); } }
    //         } else {
    //             $(this).next().slideToggle();
    //             $(this).parent().find('ul').slideUp();
    //             var curlvl = $(this).parent().data('level');
    //             if (curlvl) { $('#categories li.child-' + curlvl + ' a').removeClass('active'); }
    //         }
    //     });
  });
})(this.jQuery);
