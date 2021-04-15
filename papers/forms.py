import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, Row, HTML, ButtonHolder, Submit
from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from django_summernote.widgets import SummernoteWidget

from .custom_layout_object import Formset
from .models import *


### FILE FORMS

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']
        labels = {'file': _('Pliki')}
        help_texts = {'file': _('Pliki możesz dodać później w zakładce edycji referatu')}
        widgets = {'file': forms.ClearableFileInput(attrs={'multiple': True})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        formtag_prefix = re.sub('-[0-9]+$', '', kwargs.get('prefix', ''))

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Field('file'),
                css_class='formset_row-{}'.format(formtag_prefix)
            )
        )


UploadedFileFormSet = inlineformset_factory(Paper, UploadedFile, form=FileUploadForm,
                                            fields=['file'], extra=1, can_delete=True)


class FileAppendForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']
        labels = {'file': _('Pliki')}
        widgets = {'file': forms.ClearableFileInput(attrs={'multiple': True})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        formtag_prefix = re.sub('-[0-9]+$', '', kwargs.get('prefix', ''))

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Field('file'),
                Field('DELETE', type='hidden'),
                css_class='formset_row-{}'.format(formtag_prefix)
            )
        )


## CO AUTHOR FORMS

class CoAuthorForm(forms.ModelForm):
    class Meta:
        model = CoAuthor
        fields = ['name', 'surname', 'email']
        labels = {
            'name': _('Imię'),
            'surname': _('Nazwisko')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        formtag_prefix = re.sub('-[0-9]+$', '', kwargs.get('prefix', ''))

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Field('name'),
                Field('surname'),
                Field('email'),
                css_class='formset_row-{}'.format(formtag_prefix)
            )
        )


CoAuthorFormSet = inlineformset_factory(Paper, CoAuthor, form=CoAuthorForm,
                                        fields=['name', 'surname', 'email'], extra=1,
                                        can_delete=True)


class CoAuthorDynamicForm(forms.ModelForm):
    class Meta:
        model = Paper
        exclude = '__all__'  # If that doesn't work exclude all fields explicitly

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        coAuthors = CoAuthor.objects.filter(paper=self.instance)
        for i in range(len(coAuthors) + 1):
            name_field_name = f'coAuthor_{i}_name'
            surname_field_name = f'coAuthor_{i}_surname'
            email_field_name = f'coAuthor_{i}_email'
            self.fields[name_field_name] = forms.CharField(required=True)
            self.fields[surname_field_name] = forms.CharField(required=True)
            self.fields[email_field_name] = forms.EmailField(required=False)
            try:
                self.initial[name_field_name] = coAuthors[i].name
                self.initial[surname_field_name] = coAuthors[i].surname
                self.initial[email_field_name] = coAuthors[i].email
            except IndexError:
                self.initial[name_field_name] = ''
                self.initial[surname_field_name] = ''
                self.initial[email_field_name] = ''
        # create extra blank fields
        name_field_name = f'coAuthor_{i + 1}_name'
        surname_field_name = f'coAuthor_{i + 1}_surname'
        email_field_name = f'coAuthor_{i + 1}_email'
        self.fields[name_field_name] = forms.CharField(required=True)
        self.fields[surname_field_name] = forms.CharField(required=True)
        self.fields[email_field_name] = forms.EmailField(required=False)

    def clean(self):
        coAuthors = set()
        i = 0
        name_field_name = f'coAuthor_{i}_name'
        surname_field_name = f'coAuthor_{i}_surname'
        email_field_name = f'coAuthor_{i}_email'
        while self.cleaned_data.get(name_field_name):
            coAuthors.add([self.cleaned_data[name_field_name],
                           self.cleaned_data[surname_field_name],
                           self.cleaned_data[email_field_name]])
            i += 1
            name_field_name = f'coAuthor_{i}_name'
            surname_field_name = f'coAuthor_{i}_surname'
            email_field_name = f'coAuthor_{i}_email'
        self.cleaned_data['coAuthors'] = coAuthors

    def save(self):
        paper = self.instance
        paper.coauthor_set.all().delete()
        for coAuthor in self.cleaned_data['coAuthors']:
            CoAuthor.objects.create(name=coAuthor[0],
                                    surname=coAuthor[1],
                                    email=coAuthor[2],
                                    paper=self.instance)

    def get_coauthor_fields(self):
        for field_name in self.data:
            if field_name.startswith('coAuthor_'):
                yield self[field_name]


### PAPER FORMS

class PaperCreationForm(forms.ModelForm):
    description = forms.CharField(label='Krótki opis', widget=SummernoteWidget())

    class Meta:
        model = Paper
        fields = ['title', 'club', 'keywords', 'description']
        exclude = ['authors', 'reviewers']
        labels = dict(title=_('Tytuł'), club=_('Koło naukowe'), keywords=_('Słowa kluczowe'), description=_('Opis'))
        help_texts = dict(title=_('Tytuł'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(
                Field('title'),
                Field('club'),
                Field('keywords'),
                Field('description'),
                HTML("<br><hr>"),

                Fieldset('Współautorzy',
                         HTML("<div class='row'>"),
                         HTML("<div class='col-md-9 offset-md-2'>"),
                         Formset('coAuthors', 'papers/paper_add_author_formset.html'),
                         HTML("</div>"),
                         HTML("</div>"),
                         ),

                HTML("<hr class='my-2'>"),

                Fieldset('Pliki',
                         HTML("<div class='row'>"),
                         HTML("<div class='col-md-6 offset-md-2'>"),
                         Formset('files', 'papers/upload_files_formset.html')),
                HTML("</div>"),
                HTML("</div>"),

                HTML("<hr><br>"),
                ButtonHolder(Submit('submit', 'Dodaj')),
                HTML("<br>"),
            )
        )
        self.fields['club'].queryset = StudentClub.objects.exclude(acronym='Brak')


class PaperEditForm(forms.ModelForm):
    description = forms.CharField(label='Krótki opis', widget=SummernoteWidget())

    class Meta:
        model = Paper
        fields = ['title', 'club', 'approved', 'keywords', 'description']
        exclude = ['authors', 'reviewers']
        labels = {
            'title': _('Tytuł'),
            'club': _('Koło'),
            'approved': _('Zatwierdź'),
            'keywords': _('Słowa kluczowe'),
            'description': _('Krótki opis'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(
                Field('title'),
                Field('club'),
                Field('keywords'),
                Field('description'),

                HTML('<div class="row">'),
                Field('approved'),
                HTML('</div>'),

                HTML('<div class="row text-left ml-2">'),
                HTML('<span class="text-danger">( Pole to wskazuje recenzentowi, że referat jest gotowy )</span>'),
                HTML('</div>'),
                HTML('<hr>'),

                HTML('<div class="row>'),
                HTML('<div class="col>'),
                Fieldset('Współautorzy',
                         HTML('</div>'),
                         HTML('</div>'),

                         HTML("<br>"),
                         HTML('<div class="row offset-1">'),
                         Formset('coAuthors', 'papers/add_paper_author_formset.html')),
                HTML('</div>'),
            )
        )
        self.fields['club'].queryset = StudentClub.objects.exclude(acronym='Brak')


### REVIEW FORMS
class GradeChoiceField(forms.ModelChoiceField):
    required=True
    def label_from_instance(self, obj):
        return f'{obj.name}'


class ReviewCreationForm(forms.ModelForm):
    text = forms.CharField(label='Treść recenzji', widget=SummernoteWidget())
    correspondence = GradeChoiceField(queryset=Grade.objects.filter(tag='correspondence'))
    originality = GradeChoiceField(queryset=Grade.objects.filter(tag='originality'))
    merits = GradeChoiceField(queryset=Grade.objects.filter(tag='merits'))
    presentation = GradeChoiceField(queryset=Grade.objects.filter(tag='presentation'))
    final_grade = GradeChoiceField(queryset=Grade.objects.filter(tag='final_grade'))

    class Meta:
        model = Review
        fields = ['correspondence', 'originality', 'merits', 'presentation', 'final_grade','text']


class ReviewerChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        cnt = Paper.objects.filter(reviewers=obj).count()
        return f'{obj.first_name} {obj.last_name} ({cnt})'


class ReviewerAssignmentForm(forms.ModelForm):
    reviewers = ReviewerChoiceField(queryset=User.objects.filter(groups__name='reviewer'), label='Recenzent',
                                    required=False)

    class Meta:
        model = Paper
        fields = ['reviewers']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reviewers'].widget.attrs = {'id': 'admin-assign-reviewers-select', 'size': '10',
                                                 'class': 'custom-select'}

    def clean_reviewers(self):
        reviewers = self.cleaned_data['reviewers']
        if reviewers.count() > 2:
            raise forms.ValidationError('Nie można przypisać więcej niż dwóch recenzentów')
        return reviewers
