from django import forms
from django.utils.safestring import mark_safe
#from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape

class ButtonRadioSelect(forms.RadioSelect):
    """Radio Select with overridden renderer, placing labels after inputs.

    To make 3d stateful buttons, add CSS::

        <style type="text/css">
          ul.form-button-radio li {display: inline-block;}
          ul.form-button-radio input[type="radio"] {display: none}
          ul.form-button-radio input[type="radio"]+label {
            padding: 2px;
            border-radius: 5px;
            -moz-border-radius: 5px;
            -webkit-border-radius: 5px;
            border: 2px outset #BBB;
            cursor: pointer;
          }
          ul.form-button-radio input[type="radio"]:checked+label {
            font-weight: bold;
            background-color: #999;
            color: white;
          }
        </style>

    """

    class ButtonRadioInput(forms.widgets.RadioChoiceInput):

        def __unicode__(self):
            # No idea, why Superclass' __unicode__ does not call
            # correct render() method
            return self.render()

        def render(self, name=None, value=None, attrs=None, choices=()):
            name = name or self.name
            value = value or self.value
            attrs = attrs or self.attrs
            if 'id' in self.attrs:
                label_for = ' for="%s"' % (self.attrs['id'])
            else:
                label_for = ''
            choice_label = conditional_escape(self.choice_label)
            return mark_safe(u'%s <label%s>%s</label>' % (self.tag(), label_for, choice_label))

    class ButtonRadioFieldRenderer(forms.widgets.RadioFieldRenderer):
        def __iter__(self):
            for i, choice in enumerate(self.choices):
                yield ButtonRadioSelect.ButtonRadioInput(self.name, self.value,
                                       self.attrs.copy(), choice, i)

        def __getitem__(self, idx):
            choice = self.choices[idx] # Let the IndexError propogate
            return ButtonRadioSelect.ButtonRadioInput(self.name, self.value,
                                    self.attrs.copy(), choice, idx)

        def render(self):
            """Outputs a <ul> for this set of radio fields."""
            return mark_safe(u'<ul class="form-button-radio">\n%s\n</ul>' % u'\n'.join([u'<li>%s</li>'
                    % w for w in self]))

    renderer = ButtonRadioFieldRenderer