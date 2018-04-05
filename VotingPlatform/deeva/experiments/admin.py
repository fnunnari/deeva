from django.contrib import admin
from django.template import Context, loader
from django.forms import widgets


from .models import Experiment, Generation, Individual, VotingWizard, VariableSet, Variable, VariableRange,\
    PromotedWizard, IndividualVariableValue


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    #list
    list_display = ('id', 'name', 'created', 'independent_variables', 'dependent_variables',)
    list_display_links = ('id', 'name')

    #page
    readonly_fields = ('id', 'created', 'variables', 'download_header')

    #add more readonly fields if there is already a generation
    def get_readonly_fields(self, request, obj=None):
            if Generation.objects.filter(experiment=obj):
                return super(ExperimentAdmin, self).get_readonly_fields(request, obj) + ('independent_variables', 'dependent_variables', 'content_names')
            else:
                return super(ExperimentAdmin, self).get_readonly_fields(request, obj)

    fieldsets = (
        ('General Information', {
            'fields': ('id', 'name', 'created', 'description')
        }),
        ('Variables', {
            'fields': ('independent_variables', 'dependent_variables', 'download_header', 'variables', 'content_names',),
            #'fields': ('independent_variables', 'dependent_variables', 'variables',),
        }),
    )

    def variables(self, obj):
        template = loader.get_template('experiments/admin/admin_variables.html')
        context = {'experiment': obj}
        return template.render(context)

    variables.short_description = "Representation"

    def download_header(self, obj):
        template = loader.get_template('experiments/admin/admin_download_header.html')
        context = {'experiment': obj}
        return template.render(context)

    download_header.short_description = "Download"

    class Media:
        js = (
            'js/jquery.min.js',       
            'js/jquery.scoped.js',  
        )
    


@admin.register(Generation)
class GenerationAdmin(admin.ModelAdmin):

    #list
    list_display = ('id', 'nickname', 'experiment', 'created', 'enable_rate_retrieve', 'enable_comp_retrieve')
    list_display_links = ('id', 'nickname')

    #page
    readonly_fields = ('id', 'created', 'individuals', 'import_individuals', 'export_individuals', 'upload_content')

    fieldsets = (
        ('General Information', {
            'fields': ('id', 'nickname', 'experiment', 'created')
        }),
        ('Individuals', {
            'fields': ('import_individuals', 'export_individuals', 'upload_content',),
        }),
    )

    def import_individuals(self, obj):
        template = loader.get_template('experiments/admin/admin_upload_individuals_panel.html')
        context = {'generation': obj}
        return template.render(context)

    import_individuals.short_description = "Create"

    def export_individuals(self, obj):
        template = loader.get_template('experiments/admin/admin_export_individuals_panel.html')
        context = {'generation': obj}
        return template.render(context)

    export_individuals.short_description = "Export"

    def upload_content(self, obj):
        template = loader.get_template('experiments/admin/admin_upload_content_panel.html')
        context = {'generation': obj}
        return template.render(context)

    upload_content.short_description = "Content"

    

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('experiment',)
        return self.readonly_fields

    

class IndividualVariableValueInline(admin.TabularInline):
    model = IndividualVariableValue
    extra = 0


@admin.register(Individual)
class IndividualAdmin(admin.ModelAdmin):
    #list
    list_display = ('id', 'creation_type', 'has_content_files',)
    list_display_links = ('id',)

    #page
    readonly_fields = ('id',)

    fieldsets = (
        ('General Information', {
            'fields': ('id', 'creation_type',)
        }),
        ('Variables', {
            'fields': ('id',),#TODO
        }),
        ('Content', {
            'fields': ('has_content_files',), #TODO content preview
        }),
    )

    inlines = (IndividualVariableValueInline,)


@admin.register(VotingWizard)
class VotingWizardAdmin(admin.ModelAdmin):
    #list
    list_display = ('id', 'name', 'generation', 'enable_rating_mode', 'enable_compare_mode', 'number_of_votes', 'shown_on_overview_page', 'shown_on_overview_page', 'questions',)
    list_display_links = ('id', 'name')

    #page
    readonly_fields = ('id',)

    fieldsets = (
        ('General Information', {
            'fields': ('id', 'name', 'generation',)
        }),
        ('Configuration', {
            'fields': ('enable_rating_mode', 'enable_compare_mode', 'enable_anonymous_mode', 'number_of_votes', 'shown_on_overview_page','questions',),
        }),
        ('HTML override', {
            'fields': ('welcome_html', 'disclaimer_html', 'example_html', 'personalinfos_html', 'exit_html',),
        }),
    )

class VariableRangeInline(admin.TabularInline):
    model = VariableRange
    extra = 0


@admin.register(VariableSet)
class PersonalityProfileAdmin(admin.ModelAdmin):
    #list
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name',)

    #page
    readonly_fields = ('id',)

    inlines = (VariableRangeInline,)


@admin.register(VariableRange)
class PhysicalAttributeRangeAdmin(admin.ModelAdmin):
    pass


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    #list
    list_display = ('id', 'name', 'variable_type', 'left', 'right',)
    list_display_links = ('id', 'name')

@admin.register(IndividualVariableValue)
class IndividualVariableValueAdmin(admin.ModelAdmin):
    pass



admin.site.register(PromotedWizard)
