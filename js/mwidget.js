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
             chain.prototype = $.isFunction(base) ? base.prototype : base;
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
             var widget = this.widget(),
                 cls = widget.prototype;;

             return function dispatch(method) {
                 // usage: $(...).mwidget('method', arg ...);
                 if (typeof method == 'string') {
                     return cls.call(this, method, Array.prototype.slice.call(arguments, 1));
                 }

                 // usage: $(...).mwidget({ ... });
                 var options = method || {};
                 return this.each(function() {
                     var obj = cls.create(widget, $(this), options);
                     obj && cls.call(obj, '__init__', []);
                 });
             };
         },

         // Handle widget construction.
         create: function(type, elem, proto) {
             var data = elem.data(this.name);
             return !data && elem.data(this.name, new type(elem, proto));
         },

         // Handle widget instance methods.
         call: function(query, method, args) {
             var name = this.name,
                 self = query.data(name),
                 fn = self[method];

             // If this is a property, only act on the first element
             // in the query.
             if (fn.__property__) {
                 return fn.apply(self, args);
             }

             // This is a normal method.  Call the method on each
             // element of the query.  This for / return is equivalent
             // to `return query.each(function() { ... });'
             for (var idx = 0, lim = query.length; idx < lim; idx++) {
                 self = $.data(query[idx], name);
                 self[method].apply(self, args);
             }

             return this;
         }

     });

     // A decorator that declares a particular procedure should be
     // regarded as a property descriptor rather than a normal method.
     // See call() above.
     function property(fn) {
         fn.__property__ = true;
         return fn;
     }

     // jQuery integration

     $.defclass = defclass;

     $.mwidget = function mwidget(name, proto) {
         return (new WidgetType(name, proto || {})).method();
     };

     $.extend($.mwidget, {
         property: property
     });

})(jQuery);
