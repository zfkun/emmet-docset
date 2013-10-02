(function(){
    var each = Array.prototype.forEach;
    var curry = function(fn) {
    	var args = [].slice.call(arguments, 1);
    	return function() {
    		return fn.apply(null, args.concat([].slice.call(arguments)));
    	};
    };
    var $ = function(s, p) {
    	return typeof s === 'string' ? (p || document).querySelectorAll(s) : s;
    };
    var all = function(s, fn) {
    	return each.call($(s), fn);
    };
    var rename = function(prefix, name, n) {
        n.setAttribute('id', prefix + '_' + (name || n.innerText).replace(/\&/g, ' ').replace(/\s+/g, ' '));
    };

    all('.ch-section', function(n) {
    	var t = $('.ch-section__title', n)[0].innerText.replace(/^\s+|\s+$/g, '');
    	rename('Category', t, n);

    	//all('.ch-section__title', curry(rename, t));
    	all($('.ch-subsection__title', n), curry(rename, 'Section_' + t, ''));
    	all($('.ch-snippet__name', n), curry(rename, 'Directive_' + t, ''));
    });
})();