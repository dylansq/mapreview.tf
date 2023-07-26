// The dynamicGrid plugin code starts here - https://www.geeksforgeeks.org/how-does-inline-javascript-work-with-html/#
(function ($) {
    var methods = {

        init: function (options, elem) {
        	var $this = this;
        	this.elem = elem;
        	this.$elem = $(elem);
           this.o = $.extend({
           }, options); 
           var t = null;  
           //$this.isotopeInstance = new Isotope(this.elem, this.o.isotopeArgs);
           $(elem).isotope(this.o.isotopeArgs)
           $this.resizeColumns(); 
        	$(window).on('resize', function(){
              t = setTimeout(function(){
              	$this.resizeColumns(); 
                $(elem).isotope('layout');
              });
        	});
        },
      
      	resizeColumns: function ( ) {
          	var $items = $(this.o.itemsSelector, this.elem);
            var containerWidth = parseFloat($(this.elem).width());
            var realColumnCount = containerWidth / this.o.width;
            var floorColumnCount = Math.floor(realColumnCount);

            if (floorColumnCount <= 0){floorColumnCount = 1}

            var newItemW = Math.floor(containerWidth) / floorColumnCount;
            var newItemH = (newItemW / this.o.width) * this.o.height;
            $items.css({
                    width: Math.min(480,Math.floor(newItemW)),
                    height: Math.min(345,Math.floor(newItemH))
                });
      	}
    };
    
    if (typeof Object.create !== 'function') {
        Object.create = function (o) {
            function F() {}
            F.prototype = o;
            return new F();
        };
    }

    // Create a plugin based on a defined object
    $.plugin = function (name, object) {
        $.fn[name] = function (options) {
            return this.each(function () {
                if (!$.data(this, name)) {
                    $.data(this, name, Object.create(object).init(options, this));
                }
            });
        };
    };

    $.plugin('dynamicGrid', methods);
})(jQuery);