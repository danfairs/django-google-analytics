from django import template
from django.contrib.sites.models import Site
from django.db import models
from django.contrib.sites.models import Site

register = template.Library()
Analytics = models.get_model('googleanalytics', 'analytics')

def do_get_analytics(parser, token):
    contents = token.split_contents()
    tag_name = contents[0]
    template_name = 'google_analytics/%s_template.html' % tag_name
    if len(contents) == 2:
        # split_contents() knows not to split quoted strings.
        code = contents[1]
    elif len(contents) == 1:
        code = None
    else:
        raise template.TemplateSyntaxError, "%r cannot take more than one argument" % tag_name
   
    if not code:
        current_site = Site.objects.get_current()
    else:
        if not (code[0] == code[-1] and code[0] in ('"', "'")):
            raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
        code = code[1:-1]
        current_site = None

    return AnalyticsNode(current_site, code, template_name)
    
class AnalyticsNode(template.Node):
    def __init__(self, site=None, code=None, template_name='google_analytics/analytics_template.html'):
        self.site = site
        self.code = code
        self.template_name = template_name
        
    def render(self, context):
        content = ''
        if self.site:
            code_set = self.site.analytics_set.all()
            if code_set:
                code = code_set[0].analytics_code
            else:
                return ''
        elif self.code:
            code = self.code
        else:
            return ''
        
        if code.strip() != '':
            t = template.loader.get_template(self.template_name)
            c = template.Context({
                'analytics_code': code,
            })
            return t.render(c)
        else:
            return ''
        
register.tag('analytics', do_get_analytics)
register.tag('analytics_async', do_get_analytics)

