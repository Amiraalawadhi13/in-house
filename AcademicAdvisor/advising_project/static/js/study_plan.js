// Place this code inside study_plan.js

var formIndex = parseInt(document.getElementById('id_form-TOTAL_FORMS').value);
var totalForms = document.getElementById("id_form-TOTAL_FORMS");

function cloneMore(selector, type) {
    var newElement = $(selector).clone(true);
    var total = parseInt($(totalForms).val());
    newElement.find(':input').each(function () {
        var name = $(this).attr('name').replace('-__prefix__-', '-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({ 'name': name, 'id': id }).val('').removeAttr('checked');
    });
    total++;
    $(totalForms).val(total);
    $(selector).after(newElement);
}

function deleteForm(prefix, btn) {
    var total = parseInt($(totalForms).val());
    if (total > 1) {
        btn.closest('div').remove();
        var forms = $('.entry-form');
        $(totalForms).val(forms.length);
        for (var i = 0, formCount = forms.length; i < formCount; i++) {
            $(forms.get(i)).find(':input').each(function () {
                updateElementIndex(this, prefix, i);
            });
        }
    }
}

$(document).on('click', '.add-more', function (e) {
    e.preventDefault();
    cloneMore('#entryFormTemplate', 'form');
});

$(document).on('click', '.remove', function (e) {
    e.preventDefault();
    deleteForm('form', $(this));
});

function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

