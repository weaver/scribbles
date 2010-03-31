(function($) {
    var _body,
        _bd,
        _form,
        _fields,
        _field,
        _drag,
        _avro,
        _below_avro;

    $(document).ready(function() {
        init_fields();
        init_schema();
        init_controls();
    });

    // ---------- Controls ----------

    function init_controls() {
        $('#add-field').click(add_field);
        $('#show-schema').click(show_schema);
        $('#show-editor').click(show_editor);

        _body = $('body');
        _bd = $('#bd');
        _below_avro = $('#avro').height() - _avro.height();
    }

    function show_schema() {
        _avro.height(_bd.height() - _below_avro);
        _form.animate({
            'margin-left': '-' + _form.outerWidth() + 'px'
        }, 'fast', 'swing');
    }

    function show_editor() {
        _form.animate({
            'margin-left': '0px'
        }, 'fast', 'swing');
    }

    // ---------- Field List ----------

    function init_fields() {
        _fields = $('#fields');

        _field = _fields.children('.template')
            .remove().removeClass('template')
            .attr('draggable', 'true');

        _fields.data('item-template', _field);

        _fields
            .bind('click', click_field)
            .bind('dragstart', drag_start)
            .bind('dragend', drag_end)
            .bind('dragenter', drag_enter)
            .bind('dragover', drag_over)
            .bind('drop', drop);
    }

    function add_field() {
        var field = _field.clone().appendTo(_fields);
        _body.attr('scrollTop', _body.attr('scrollHeight'));
        _form.change();
    }

    function remove_field(field) {
        field.remove();
        _form.change();
    }

    function click_field(ev) {
        var target = $(ev.target);
        if (target.is('.remove')) {
            remove_field(target.up('.field'));
        }
    }

    function field(obj) {
        return $(obj).up('.field');
    }

    function drag_start(ev) {
        _drag = $(ev.target).addClass('drag');
        ev.originalEvent.dataTransfer.setData('FireFox', 'requires this');
        return true;
    }

    function drag_end(ev) {
        $(ev.target).removeClass('drag')
            .siblings().andSelf().removeClass('over');
    }

    function drag_enter(ev) {
        field(ev.target)
            // Do this here instead of dragleave because of the order
            // WebKit fires events for nested elements.
            .siblings('.over').removeClass('over').end()
            .addClass('over');
    }

    function is_drop(elem) {
        return (elem != _drag[0]) && (elem.parentNode == _drag[0].parentNode);
    }

    function drag_over(ev) {
        // Return "false" if dropping is allowed.
        return !is_drop(field(ev.target).get(0));
    }

    function drop(ev) {
        // Place the dragged node on the "other side" of the drop
        // target depending on their relative position.
        var drop = field(ev.target).removeClass('over');
        drop[(drop.index() > _drag.index()) ? 'after' : 'before'](_drag);
        _drag = undefined;
        _form.change();
        return false;
    }

    // ---------- Editor / Textarea ----------

    function init_schema() {
        _form = $('#record').change(on_editor_change);
        _avro = $('#avro textarea').change(on_schema_change);
        _avro.change();
    }

    function on_editor_change(ev) {
        store(_form.value());
    }

    function on_schema_change(ev) {
        store(update_editor(load(_avro.val())));
    }

    function load(data) {
        try {
            return JSON.parse(data);
        }
        catch(exn) {
            alert('Load Error: ' + exn);
            throw exn;
        }
    }

    function store(obj) {
        _avro.val(JSON.stringify(obj, undefined, 2));
    }

    function update_editor(obj) {
        _form.value(obj);
        return obj;
    }

    // The value of a maybe-list may be:
    //   "", "foo", or ["foo", "bar", ...]
    $.fn.value.get('maybe-list', function(input) {
        var val = input.val();
        if (!val || val.length == 0) {
            return "";
        }
        else if (val.length == 1) {
            return val[0];
        }
        else {
            return val;
        }
    });

})(jQuery);