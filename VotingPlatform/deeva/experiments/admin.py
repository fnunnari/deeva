from django.contrib import admin
from django.template import Context, loader
from django.forms import widgets


from .models import Experiment, Generation, Individual, VotingWizard, VariableSet, Variable, VariableRange,\
    PromotedWizard, IndividualVariableValue, CompareVote, RateVote


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
    readonly_fields = ('id', 'created', 'individuals', 'generate_individuals', 'import_individuals', 'export_individuals', 'upload_content')

    fieldsets = (
        ('General Information', {
            'fields': ('id', 'nickname', 'experiment', 'created',)
        }),
        ('Individuals', {
            'fields': ('generate_individuals', 'import_individuals', 'export_individuals', 'upload_content',),
        }),
    )

    def generate_individuals(self, obj):
        template = loader.get_template('experiments/admin/admin_generate_individuals_panel.html')
        context = {'generation': obj}
        return template.render(context)

    generate_individuals.short_description = "Generate"

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
    list_display = ('id', 'name', 'generation', 'enable_rating_mode', 'enable_compare_mode', 'number_of_votes', 'shown_on_overview_page', 'questions',)
    list_display_links = ('id', 'name')

    #page
    readonly_fields = ('id','export','wizard_links',)

    fieldsets = (
        ('General Information', {
            'fields': ('id', 'name', 'generation',)
        }),
        ('Configuration', {
            'fields': ('enable_rating_mode', 'enable_compare_mode', 'enable_anonymous_mode', 'number_of_votes', 'consistency_check', 'forced_break', 'size_of_content', 'shown_on_overview_page', 'distraction_free_mode', 'questions',),
        }),
        ('HTML override', {
            'fields': ('welcome_html', 'disclaimer_html', 'example_html', 'rate_vote_html', 'break_html', 'personalinfos_html', 'exit_html',),
        }),
        ('Other', {
            'fields': ('export','wizard_links',),
        }),

    )

    def export(self, obj):
        template = loader.get_template('experiments/admin/admin_export_ratevotes_panel.html')
        context = {'wizard': obj}
        return template.render(context)

    def wizard_links(self, obj):
        template = loader.get_template('experiments/admin/admin_wizard_links_panel.html')
        context = {'wizard': obj}
        return template.render(context)

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




@admin.register(RateVote)
class RateVoteAdmin(admin.ModelAdmin):
    #list
    list_display = ('id', 'user', 'individual', 'variable', 'text_value', 'consistency', 'generation', 'wizard')
    list_display_links = ('id',)

    list_filter = ('wizard', 'generation',)

    #page
    readonly_fields = ('date_time',)


admin.site.register(CompareVote)
admin.site.register(PromotedWizard)