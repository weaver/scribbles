/// jQuery.mwidget -- A miniature jQuery widget protocol.
/// http://orangesoda.net/jquery.mwidget.html

/// Copyright (c) 2009, Ben Weaver.  All rights reserved.
/// This software is issued "as is" under a BSD license
/// <http://orangesoda.net/license.html>.  All warranties disclaimed.

(function($) {

     function defclass(base, proto) {
         var constructor;

         // usage: defclass({ ... });
         if (proto === undefined) {
             // There is no base class; use an "identity" prototype
             // constructor to make a prototype chain that looks like
             // this: (instance -> proto).
             proto = base;
             function chain() { return proto; };
         }
         // usage: defclass(class, { ... });
         else {
             // There is a base class; link proto and base together
             // like this: (instance -> proto -> base).
             function chain() { $.extend(this, proto); };
             chain.prototype = base;
         }

         // Pop `__new__' out of the class definition.  Use it as
         // the constructor.
         constructor = proto.__new__;
         delete proto.__new__;
         constructor.prototype = new chain();

         return constructor;
     }

     // The principle concern of a WidgetType is creating Widget
     // classes and jQuery methods.
     var WidgetType = defclass({

         __new__: function WidgetType(name, proto) {
             this.name = name;
             $.extend(this, proto);
         },

         // Derive a Widget constructor from this type.
         widget: function() {
             return defclass(this, $.extend({
                 __new__: function Widget(elem, proto) {
                     this.elem = elem;
                     $.extend(this, proto);
                 }
             }, this.template));
         },

         // This template is used to extend a Widget prototype.  Add
         // widget attributes here that cannot be added in the
         // WidgetType prototype.  It is simpler not to use this.
         template: null,

         // Create a jQuery method for this WidgetType; dispatch to
         // `create()' or `call()'.
         method: function() {
             var meta = this,
                 wtype = this.widget();

             return function dispatch(options) {
                 // usage: $(...).mwidget('method', arg ...);
                 if (typeof options == 'string') {
                     return meta.call(this, options, Array.prototype.slice.call(arguments, 1));
                 }

                 // usage: $(...).mwidget({ ... });
                 options = options || {};
                 return this.each(function() {
                     meta.call(meta.create(wtype, $(this), options), '__init__', []);
                 });
             };
         },

         // Handle widget construction.
         create: function(widget, elem, proto) {
             return elem.data(this.name, new widget(elem, proto));
         },

         // Handle widget instance methods.
         call: function(elem, method, args) {
             var self = elem.data(this.name),
                 fn = self[method];

             // Methods are called as fn(self, arg ...)
             args.unshift(self);
             return fn.apply(null, args);
         }
     });

     // jQuery integration
     $.defclass = defclass;
     $.mwidget = function mwidget(name, proto) {
         return (new WidgetType(name, proto || {})).method();
     };

})(jQuery);
