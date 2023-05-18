(function($){
    jQuery.fn.embedVideo = function(pluginOptions) {
        return this.each(function() {
            var defaultOptions = {};
            for (var key in pluginMethods.defaultOptions) {
                defaultOptions[key] = pluginMethods.defaultOptions[key];
            }

            var containerOptions = $.extend(defaultOptions, pluginOptions, $(this).data());
            pluginMethods.init.apply(this, [containerOptions]);
        });
    };

    var pluginMethods = {
        defaultOptions : {
            sizePreview: '',
            autoSizePreview: true,
            alternativeCover: false,
            imagePlayContainer: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 428.41 301.36" height="50"><path d="M639.64,440.2l115.76-60-115.76-60.4Z" transform="translate(-469.68 -233.97)" fill="#fff"/><path d="M893.81,299s-4.19-29.53-17-42.53c-16.27-17.07-34.56-17.16-42.9-18.16C773.9,234,684,234,684,234h-.17s-89.92,0-149.9,4.32c-8.35,1-26.64,1.09-42.91,18.16-12.84,13-17,42.53-17,42.53a647.81,647.81,0,0,0-4.28,69.33v32.51A648.06,648.06,0,0,0,474,470.15s4.19,29.53,17,42.53c16.31,17.07,37.71,16.53,47.23,18.33,34.26,3.27,145.67,4.32,145.67,4.32s90-.13,150-4.49c8.38-1,26.63-1.09,42.9-18.16,12.84-13,17-42.53,17-42.53a649,649,0,0,0,4.28-69.33V368.31A647.81,647.81,0,0,0,893.81,299ZM639.64,440.2V319.82l115.76,60.4Z" transform="translate(-469.68 -233.97)" fill="#e52d27"/></svg>',

            imagePlayOpacity: .85,
            callback: function() {},
            listType: '',
            list: '',
            autoplay: 1,
            cc_load_policy: 0,
            color: 'red',
            controls: 1,
            disablekb: 0,
            enablejsapi: 0,
            end: '',
            fs: 1,
            hl: '',
            iv_load_policy: 1,
            loop: 0,
            modestbranding: 0,
            origin: '',
            playlist: '',
            playsinline: 0,
            rel: 1,
            showinfo: 1,
            start: 0
        },

        autoSizePreview : function(containerWidth, options) {

            var isDetect = false;
            $.each({
                120  : 'default',
                320  : 'mqdefault',
                480  : 'hqdefault',
                640  : 'sddefault',
                1280 : 'maxresdefault'
            }, function(width, preview){
                if (containerWidth < width && isDetect === false) {
                    options.sizePreview = preview;
                    isDetect = true;
                }
            });

            // return options;
        },

        replacePlayer : function($this, options)
        {
            var query = pluginMethods.queryBuild(options);
            $this.html('<iframe src="https://www.youtube.com/embed/'+ options.id +'?'+query+'" width="100%" height="100%" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>');
            options.callback.call($this, $this.find('iframe')[0]);
        },

        queryBuild: function(options)
        {
            
            var skip = ['callback', 'sizePreview', 'autoSizePreview', 'alternativeCover', 'imagePlayContainer', 'imagePlayOpacity'];

            var query = [];
            $.each(options, function(key, value){
                if (skip.indexOf(key) == -1 && value !== '') {
                    query.push(key + '=' + value);
                }
            });

            return query.join('&');
        },

        init: function(options) {
            var $this = $(this),
                height = $this.height(),
                width = $this.attr('width');
            
            if (true) {
                width = $this.attr('width');
            }

            if (height == 0) {
                height = $this.attr('height');
            }
            console.log(height,width)
            
            if (options.autoSizePreview && options.sizePreview == '') {
                pluginMethods.autoSizePreview(width, options);
            }

            
            var previewFile = 'https://img.youtube.com/vi/'+ options.id +'/'+ options.sizePreview +'.jpg';
            if (options.alternativeCover !== false) {
                previewFile = options.alternativeCover;
            }

            
            $this.css({
                'background' : '#000 url('+previewFile+') center',
                'background-size' : 'cover',
                width:  width,
                height: height
            });

            
            var $clickContainer = $('<a href="javascript:void(0);">'+options.imagePlayContainer+'</a>').css({
                display: 'flex',
                'justify-content': 'center',
                'align-items': 'center',
                width: '100%',
                height: 'inherit',
                opacity: options.imagePlayOpacity
            }).hover(function(){
                $(this).stop(true, true).animate({opacity: 1}, 170);
            }, function(){
                $(this).stop(true, true).animate({opacity: options.imagePlayOpacity}, 170);
            });

            $clickContainer.click(function(){
                $(this).animate({opacity: 0}, 80, function(){
                    pluginMethods.replacePlayer($this, options);
                    $(this).remove();
                });
            });

            $this.append($clickContainer);
        }
    };
})(jQuery);