(function($) {
  "use strict";
  $(document).ready(function() {
    $("#open-switcher").click(function() {
      $("#style-switcher").toggleClass('show');
      $("#settings").toggle();
      $(this).toggleClass('toggle');
      $(this).find('i').toggleClass('left');
    });
    var opts = {
      auto: {
        speed: 3500,
        pauseOnHover: true
      },
      fullScreen: false,
      swipe: false,
    };
    makeBSS('.bss-slides', opts);
    // $('.top-bar-dropdown').click(function(event) {
    //     $('.top-bar-dropdown').not(this).removeClass('active');
    //     if ($(event.target).parent().parent().attr('class') == 'options') {
    //         hideDD();
    //     } else {
    //         if ($(this).hasClass('active') && $(event.target).is("span")) {
    //             hideDD();
    //         } else {
    //             $(this).toggleClass('active');
    //         }
    //     }
    //     event.stopPropagation();
    // });
    // $(document).click(function() {
    //     hideDD();
    // });
    // $('ul.options li').click(function() {
    //     var opt = $(this);
    //     var text = opt.text();
    //     $('.top-bar-dropdown.active span').text(text);
    //     hideDD();
    // });

    // function hideDD() {
    //     $('.top-bar-dropdown').removeClass('active');
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
    // $('ul.menu').superfish({
    //     delay: 400,
    //     speed: 200,
    //     speedOut: 100,
    //     autoArrows: true
    // });
    // var jPanelMenu = $.jPanelMenu({
    //     menu: '#responsive',
    //     animated: true,
    //     keyboardShortcuts: true
    // });
    // jPanelMenu.on();
    // $(document).on('click', jPanelMenu.menu + ' li a', function(e) {
    //     if (jPanelMenu.isOpen() && $(e.target).attr('href').substring(0, 1) === '#') {
    //         jPanelMenu.close();
    //     }
    // });
    $(document).on('touchend click', '.menu-trigger', function(e) {
      // jPanelMenu.trigger();
      $(".menu").toggleClass("responsive");
      e.preventDefault();
      return false;
    });
    // $('#jPanelMenu-menu').removeClass('menu');
    // $('ul#jPanelMenu-menu li').removeClass('dropdown');
    // $('ul#jPanelMenu-menu li ul').removeAttr('style');
    // $('ul#jPanelMenu-menu li div').removeClass('mega');
    // $('ul#jPanelMenu-menu li div').removeAttr('style');
    // $('ul#jPanelMenu-menu li div div').removeClass('mega-container');
    // $(window).resize(function() {
    //     var winWidth = $(window).width();
    //     if (winWidth > 767) {
    //         jPanelMenu.close();
    //     }
    // });
    // $('.tp-banner').revolution({
    //     delay: 9000,
    //     startwidth: 1290,
    //     startheight: 380,
    //     minHeight: 480,
    //     hideThumbs: 10,
    //     hideTimerBar: "on",
    //     onHoverStop: "on",
    //     navigationType: "none",
    //     fullScreen: "on",
    //     fullScreenAlignForce: "on",
    //     fullWidth: "off",
    //     touchenabled: "on",
    //     soloArrowLeftHOffset: 0,
    //     soloArrowLeftVOffset: 0,
    //     soloArrowRightHOffset: 0,
    //     soloArrowRightVOffset: 0
    // });
    // $('#new-arrivals').showbizpro({
    //     dragAndScroll: "off",
    //     visibleElementsArray: [4, 4, 3, 1],
    //     carousel: "off",
    //     entrySizeOffset: 0,
    //     allEntryAtOnce: "off",
    //     rewindFromEnd: "off",
    //     autoPlay: "off",
    //     delay: 2000,
    //     speed: 400,
    //     easing: 'Back.easeOut'
    // });
    // $('#happy-clients').showbizpro({
    //     dragAndScroll: "off",
    //     visibleElementsArray: [1, 1, 1, 1],
    //     carousel: "off",
    //     entrySizeOffset: 0,
    //     allEntryAtOnce: "off"
    // });
    // $('#our-clients').showbizpro({
    //     dragAndScroll: "off",
    //     visibleElementsArray: [5, 4, 3, 1],
    //     carousel: "off",
    //     entrySizeOffset: 0,
    //     allEntryAtOnce: "off"
    // });
    $(".parallax-banner").pureparallax({
        overlayBackgroundColor: '#000',
        overlayOpacity: '0.45',
        timeout: 0
    });
    // $(".parallax-titlebar").pureparallax({
    //     timeout: 0
    // });

    function addLevelClass($parent, level) {
      $parent.addClass('parent-' + level);
      var $children = $parent.children('li');
      $children.addClass('child-' + level).data('level', level);
      $children.each(function() {
        var $sublist = $(this).children('ul');
        if ($sublist.length > 0) {
          $(this).addClass('has-sublist');
          addLevelClass($sublist, level + 1);
        }
      });
    }
    addLevelClass($('#categories'), 1);
    // $('#.categories > li a').click(function(e) {
    $('.open_nav').click(function(e) {
      //add click on icon
      if ($(this).parent().hasClass('has-sublist')) {
        e.preventDefault();
      }
      if ($(this).attr('class') != 'active') {
        $(this).parent().siblings().find('ul').slideUp();
        $(this).next().slideToggle();
      } else {
        $(this).next().slideToggle();
        $(this).parent().find('ul').slideUp();
      }
    });
    // $('.top_nav').click(function(e) {
    //     //add click on icon
    //     // var icon = $(this);
    //     $('.top_nav.caret').css('display', 'none');
    //     if ($(this).parent().hasClass('has-sublist')) {
    //         e.preventDefault();
    //     }
    //     if ($(this).attr('class') != 'active') {
    //         $(this).parent().siblings().find('ul').slideUp();
    //         $(this).next().slideToggle('start', function () {
    //                 $('.top_nav.caret').css('display', 'inherit');
    //        });
    //         if ($(this).parent().hasClass("has-sublist")) {
    //             // $(this).parent().siblings().find('a').removeClass('active');
    //             // $(this).addClass('active');
    //         } else {
    //             var curlvl = $(this).parent().data('level');
    //             if (curlvl) {
    //                 // $('#.categories li.child-' + curlvl + ' a').removeClass('active');
    //             }
    //         }
    //     } else {
    //         $(this).next().slideToggle('start', function () {
    //                 $('.top_nav.caret').css('display', 'inherit');
    //        });
    //         $(this).parent().find('ul').slideUp();
    //         var curlvl = $(this).parent().data('level');
    //         if (curlvl) {
    //             // $('#.categories li.child-' + curlvl + ' a').removeClass('active');
    //         }
    //     }
    // });
    $("#slider-range").slider({
      range: true,
      min: 0,
      max: 100,
      values: [0, 100],
      slide: function(event, ui) {
        event = event;
        $("#amount").val("rub" + ui.values[0] + " - rub" + ui.values[1]);
      }
    });
    $("#amount").val("rub" + $("#slider-range").slider("values", 0) + " - rub" + $("#slider-range").slider("values", 1));
    $("#slider-range-alt").slider({
      range: true,
      min: 0,
      max: 500,
      values: [0, 500],
      slide: function(event, ui) {
        event = event;
        $("#amount").val("rub" + ui.values[0] + " - rub" + ui.values[1]);
      }
    });
    $("#amount").val("rub" + $("#slider-range").slider("values", 0) + " - rub" + $("#slider-range").slider("values", 1));
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
    // $('#product-slider-vertical').royalSlider({
    //     autoScaleSlider: true,
    //     autoScaleSliderWidth: 560,
    //     autoHeight: true,
    //     loop: false,
    //     slidesSpacing: 0,
    //     imageScaleMode: 'none',
    //     imageAlignCenter: false,
    //     navigateByClick: false,
    //     numImagesToPreload: 2,
    //     arrowsNav: true,
    //     arrowsNavAutoHide: false,
    //     arrowsNavHideOnTouch: true,
    //     keyboardNavEnabled: true,
    //     fadeinLoadedSlide: true,
    //     controlNavigation: 'thumbnails',
    //     thumbs: {
    //         orientation: 'vertical',
    //         firstMargin: false,
    //         appendSpan: true,
    //         autoCenter: false,
    //         spacing: 10,
    //         paddingTop: 10,
    //     }
    // });
    // $('#basic-slider').royalSlider({
    //     autoScaleSlider: true,
    //     autoScaleSliderHeight: "auto",
    //     autoHeight: true,
    //     loop: false,
    //     slidesSpacing: 0,
    //     imageScaleMode: 'none',
    //     imageAlignCenter: false,
    //     navigateByClick: false,
    //     numImagesToPreload: 2,
    //     arrowsNav: true,
    //     arrowsNavAutoHide: false,
    //     arrowsNavHideOnTouch: true,
    //     keyboardNavEnabled: true,
    //     fadeinLoadedSlide: true,
    // });
    var thisrowfield;
    $('.qtyplus').click(function(e) {
      e.preventDefault();
      console.log('plus');
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
      console.log('minus');
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
    var $accor = $('.accordion');
    $accor.each(function() {
      $(this).addClass('ui-accordion ui-widget ui-helper-reset');
      $(this).find('h3').addClass('ui-accordion-header ui-helper-reset ui-state-default ui-accordion-icons ui-corner-all');
      $(this).find('div').addClass('ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom');
      $(this).find("div").hide().first().show();
      $(this).find("h3").first().removeClass('ui-accordion-header-active ui-state-active ui-corner-top').addClass('ui-accordion-header-active ui-state-active ui-corner-top');
      $(this).find("span").first().addClass('ui-accordion-icon-active');
    });
    var $trigger = $accor.find('h3');
    $trigger.on('click', function(e) {
      var location = $(this).parent();
      if ($(this).next().is(':hidden')) {
        var $triggerloc = $('h3', location);
        $triggerloc.removeClass('ui-accordion-header-active ui-state-active ui-corner-top').next().slideUp(300);
        $triggerloc.find('span').removeClass('ui-accordion-icon-active');
        $(this).find('span').addClass('ui-accordion-icon-active');
        $(this).addClass('ui-accordion-header-active ui-state-active ui-corner-top').next().slideDown(300);
      }
      e.preventDefault();
    });
    $(".toggle-container").hide();
    $(".trigger").toggle(function() {
      $(this).addClass("active");
    }, function() {
      $(this).removeClass("active");
    });
    $(".trigger").click(function() {
      $(this).next(".toggle-container").slideToggle();
    });
    $(".trigger.opened").toggle(function() {
      $(this).removeClass("active");
    }, function() {
      $(this).addClass("active");
    });
    $(".trigger.opened").addClass("active").next(".toggle-container").show();
    $('.counter').counterUp({
      delay: 10,
      time: 2000
    });
    $("a.close").removeAttr("href").click(function() {
      $(this).parent().fadeOut(200);
    });
    $(".tooltip.top").tipTip({
      defaultPosition: "top"
    });
    $(".tooltip.bottom").tipTip({
      defaultPosition: "bottom"
    });
    $(".tooltip.left").tipTip({
      defaultPosition: "left"
    });
    $(".tooltip.right").tipTip({
      defaultPosition: "right"
    });
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
    if ($('#skillzz').length !== 0) {
      var skillbar_active = false;
      $('.skill-bar-value').hide();
      if ($(window).scrollTop() === 0 && isScrolledIntoView($('#skillzz')) === true) {
        skillbarActive();
        skillbar_active = true;
      } else if (isScrolledIntoView($('#skillzz')) === true) {
        skillbarActive();
        skillbar_active = true;
      }
      $(window).bind('scroll', function() {
        if (skillbar_active === false && isScrolledIntoView($('#skillzz')) === true) {
          skillbarActive();
          skillbar_active = true;
        }
      });
    }

    function isScrolledIntoView(elem) {
      var docViewTop = $(window).scrollTop();
      var docViewBottom = docViewTop + $(window).height();
      var elemTop = $(elem).offset().top;
      var elemBottom = elemTop + $(elem).height();
      return ((elemBottom <= (docViewBottom + $(elem).height())) && (elemTop >= (docViewTop - $(elem).height())));
    }

    function skillbarActive() {
      setTimeout(function() {
        $('.skill-bar-value').each(function() {
          $(this).data("origWidth", $(this)[0].style.width).css('width', '1%').show();
          $(this).animate({
            width: $(this).data("origWidth")
          }, 1200);
        });
        $('.skill-bar-value .dot').each(function() {
          var me = $(this);
          var perc = me.attr("data-percentage");
          var current_perc = 0;
          var progress = setInterval(function() {
            if (current_perc >= perc) {
              clearInterval(progress);
            } else {
              current_perc += 1;
              me.text((current_perc) + '%');
            }
          }, 10);
        });
      }, 10);
    }
    $('.orderby').selectric();
    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ? true : false;
    $(".variables select").each(function() {
      if (!isMobile) {
        var sb = new SelectBox({
          selectbox: $(this)
        });
        void(sb);
      }
    });
    if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
      $(".variables select").css({
        'display': 'block'
      });
    }
    $('.option-set li').click(function(event) {
      event.preventDefault();
      var item = $(".og-grid li"),
        image = item.find('a.grid-item-image img');
      item.removeClass('clickable unclickable');
      image.stop().animate({
        opacity: 1
      });
      var filter = $(this).children('a').data('filter');
      item.filter(filter).addClass('clickable');
      item.filter(':not(' + filter + ')').addClass('unclickable');
      item.filter(':not(' + filter + ')').find('a.grid-item-image im').stop().animate({
        opacity: 0.2
      });
    });
    PureGrid.init();
    // var pixelRatio = !!window.devicePixelRatio ? window.devicePixelRatio : 1;
    // $(window).on("load", function() {
    //     if (pixelRatio > 1) {
    //         $('#logo img').each(function() {
    //             $(this).attr('src', $(this).attr('src').replace(".", "@2x."));
    //         });
    //     }
    // });
    $(window).load(function() {
      var $container = $('#portfolio-wrapper, #masonry-wrapper');
      $container.isotope({
        itemSelector: '.portfolio-item, .masonry-item',
        layoutMode: 'masonry',
        filter: $('#filters a.selected').attr('data-filter')
      });
    });
    $('#filters a').click(function(e) {
      e.preventDefault();
      var selector = $(this).attr('data-filter');
      $('#portfolio-wrapper').isotope({
        filter: selector
      });
      $(this).parents('ul').find('a').removeClass('selected');
      $(this).addClass('selected');
    });
    var $Filter = $('.share-buttons');
    var FilterTimeOut;
    $Filter.find('ul li:first').addClass('active');
    $Filter.find('ul li:not(.active)').hide();
    $Filter.hover(function() {
      clearTimeout(FilterTimeOut);
      if ($(window).width() < 959) {
        return;
      }
      FilterTimeOut = setTimeout(function() {
        $Filter.find('ul li:not(.active)').stop(true, true).animate({
          width: 'show'
        }, 250, 'swing');
        $Filter.find('ul li:first-child a').addClass('share-hovered');
      }, 100);
    }, function() {
      if ($(window).width() < 960) {
        return;
      }
      clearTimeout(FilterTimeOut);
      FilterTimeOut = setTimeout(function() {
        $Filter.find('ul li:not(.active)').stop(true, true).animate({
          width: 'hide'
        }, 250, 'swing');
        $Filter.find('ul li:first-child a').removeClass('share-hovered');
      }, 250);
    });
    // $('.responsive-table').stacktable();
    //fix cart table input issues
    // $(document).on('change', 'input[name^=items]', function() {
    //   var name = $(this).attr('name')
    //   var type = name.split('-')[2];
    //   var $inputs = $('input[name=' + name);
    //   if (type == 'DELETE')
    //     $inputs.prop('checked', $(this).prop('checked'));
    //   else {
    //     var tmp = $(this).val();
    //     $inputs.each(function() {
    //       $(this).val(tmp);
    //     })
    //   }
    //   // $('input[name=items-0-DELETE]')
    //   // console.log('test');
    // });
    // $(document).on('change', 'input[name=items-0-DELETE]', function() {
    //     $('input[name=items-0-DELETE]').prop('checked', $(this).prop('checked'));
    // });

    $(window).resize(function() {
      if ($(window).width() < 960) {
        $Filter.find('ul li:not(.active)').show();
      } else {
        $Filter.find('ul li:not(.active)').hide();
      }
    });
    $(window).resize();


    var pxShow = 600;
    var fadeInTime = 400;
    var fadeOutTime = 400;
    var scrollSpeed = 400;
    jQuery(window).scroll(function() {
      if (jQuery(window).scrollTop() >= pxShow) {
        jQuery("#backtotop").fadeIn(fadeInTime);
      } else {
        jQuery("#backtotop").fadeOut(fadeOutTime);
      }
    });
    jQuery('#backtotop a').click(function() {
      jQuery('html, body').animate({
        scrollTop: 0
      }, scrollSpeed);
      return false;
    });
    // $('a.advanced-search-btn').click(function(e) {
    //     e.preventDefault();
    //     $('.woo-search-elements').toggleClass('active');
    // });
    //     $("#contactform .submit").click(function(e) {
    //         e.preventDefault();
    //         var user_name = $('input[name=name]').val();
    //         var user_email = $('input[name=email]').val();
    //         var user_comment = $('textarea[name=comment]').val();
    //         var proceed = true;
    //         if (user_name === "") {
    //             $('input[name=name]').addClass('error');
    //             proceed = false;
    //         }
    //         if (user_email === "") {
    //             $('input[name=email]').addClass('error');
    //             proceed = false;
    //         }
    //         if (user_comment === "") {
    //             $('textarea[name=comment]').addClass('error');
    //             proceed = false;
    //         }
    //         if (proceed) {
    //             $('.hide').fadeIn();
    //             $("#contactform .submit").fadeOut();
    //             var post_data = {
    //                 'userName': user_name,
    //                 'userEmail': user_email,
    //                 'userComment': user_comment
    //             };
    //             $.post('contact.php', post_data, function(response) {
    //                 var output;
    //                 if (response.type == 'error') {
    //                     output = '<div class="error">' + response.text + '</div>';
    //                     $('.hide').fadeOut();
    //                     $("#contactform .submit").fadeIn();
    //                 } else {
    //                     output = '<div class="success">' + response.text + '</div>';
    //                     $('#contact div input').val('');
    //                     $('#contact textarea').val('');
    //                     $('.hide').fadeOut();
    //                     $("#contactform .submit").fadeIn().attr("disabled", "disabled").css({
    //                         'backgroundColor': '#c0c0c0',
    //                         'cursor': 'default'
    //                     });
    //                 }
    //                 $("#result").hide().html(output).slideDown();
    //             }, 'json');
    //         }
    //     });
    //     $("#contactform input, #contactform textarea").keyup(function() {
    //         $("#contactform input, #contactform textarea").removeClass('error');
    //         $("#result").slideUp();
    //     });
    function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
      // these HTTP methods do not require CSRF protection
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
      }
    });
    $('.product-button').click(function(event) {
      event.preventDefault();
      var data = $(this);
      $.ajax({
        url: $(data).attr('href'),
        type: "POST",
        data: {
          'product_id': $(this).attr('product-id')
        },
        beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
          $('.cart-btn').hide();
          $('.loader').show();
        },
        success: function(data) {
          if (data.error == true) {
            $('.cart-btn').show();
            $('.loader').hide();
          } else {
            $('.loader').hide();
            $('.cart-draw').html(data);
          }
        },
        error: function(data) {
          $('.cart-btn').show();
          $('.loader').hide();
        }
      });
      $(this).addClass('added');
      $(this).text('В корзине');
    });

  });
})(this.jQuery);
