(function($) {

    // Starting with the current query, try to match the selector
    // otherwise try parent().
    $.fn.up = function(sel) {
        var item = this;
        while (item && !item.is(sel)) {
            item = item.parent();
        }
        return item;
    };

    // down() -- a shallow find/each
    //
    // Walk downward, until the selector is matched.  Call fn() on
    // matched each matched item.  Don't traverse into matched item.
    $.fn.down = function(sel, fn) {
        var queue = this.get(),
            elem, item, idx, lim;

        while (queue.length > 0) {
            elem = queue.shift();
            item = $(elem);
            if (!item.is(sel))
                $.merge(queue, item.children());
            else if (false === fn.call(queue[idx], item))
                break;
        }

        return this;
    };

    // Return the name of the first query item.
    $.fn.name = function() {
        return this.attr('name') || this.attr('data-name');
    };

    // Add a ":named" pseudo-selector that works like
    $.expr.filters.named = function(elem) {
        return !!(elem.getAttribute('name')
                  || elem.getAttribute('data-name'));
    };

    $.fn.value = function(value) {
        if (value === undefined)
            return getval(this);
        else if (this.length < 2)
            return setval(this, value);
        return this.each(function(_, item) {
            setval($(item), value);
        });
    };

    // defrole() -- define a generic role-method over a WAI-ARIA role.
    //
    // A role is a space-separated list of types from most specific to
    // least specific.  A role-method is a registry of methods for
    // individual types.  When it is called on an element, the most
    // specific role-method that matches the element is called.
    $.defrole = function(registry) {
        var cache;

         registry = registry || {};
         if ($.isFunction(registry)) {
             registry = { undefined: registry };
         }

        // Keep a cache of roles that aren't defined directly in the
        // registry.  When a cache miss occurs, the role is scanned
        // for the most specific match by dispatch().
        function Cache() {}
        Cache.prototype = registry;

        // Clear the cache.
        function clear() {
            cache = new Cache();
        }

        // The dispatch method is returned by defrole().  It tries to
        // look up the role in the cache and falls back to scanning.
        function dispatch(elem) {
            var role = elem.attr('role');
            if (role === undefined)
                return cache[undefined].apply(cache, arguments);

            var probe = cache[role];
            if (!probe) {
                $.each(role.split(/\s+/), function(_, key) {
                    probe = cache[key];
                    return probe !== undefined;
                });
                probe = cache[role] = probe || cache[undefined];
            }
            return probe.apply(cache, arguments);
        };

        // A define() method is attached to the dispatcher for future
        // extension.  The cache is cleared in case a more specific
        // method has been defined.
        dispatch.define = function(key, op) {
            clear();
            registry[key] = op;
            return op;
        };

        clear(); // Prime the cache.
        return dispatch;
    };

    // getval() -- create a JSON value from a structured set of form
    // inputs.
    var getval = $.defrole({
        undefined: function(query) {
            return query.is(':input') ? query.val() : this.object(query);
        },

        object: function(query) {
            var obj = {};

            query.down(':named', function(input) {
                obj[input.name()] = getval(input);
            });

            return obj;
        },

        list: function(input) {
            var result = [];
            input.children().each(function(idx, item) {
                result.push(getval($(item)));
            });
            return result;
        }
    });

    // setval() -- set the value of a structured input using a JSON
    // object.
    var setval = $.defrole({
        undefined: function(query, obj) {
            return query.is(':input') ? query.val(obj) : this.object(query, obj);
        },

        object: function(query, obj) {
            var inputs = map_named(query);

            $.each(obj, function(key, val) {
                if (key in inputs)
                    setval(inputs[key], val);
            });

            return query;
        },

        list: function(input, obj) {
            // FIXME: hacky
            var tpl = input.empty().data('item-template');
            $.each(obj, function(index, field) {
                input.append(setval(tpl.clone(), field));
            });
            return input;
        }
    });

    // Make a mapping of {name: input} :named items that are down()
    // from query.
    function map_named(query) {
        var result = {};
        query.down(':named', function(input) {
            result[input.name()] = input;
        });
        return result;
    }

    $.fn.value.get = getval.define;
    $.fn.value.set = setval.define;

})(jQuery);
