from flask import Flask, render_template
from flask.ext.wtf import Form
from wtforms import widgets, SelectMultipleField

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class SimpleForm(Form):
        checkboxes = MultiCheckboxField('Playlists', coerce=int)
