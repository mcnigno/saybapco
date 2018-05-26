from flask import render_template, redirect
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, IndexView, BaseView, expose, MasterDetailView, DirectByChartView, GroupByChartView
from app import appbuilder, db
from .models import Document, Comments, Revisions
from helpers import comments, check_Doc, check_reply
from flask_appbuilder.widgets import ListBlock, ListCarousel, ListMasterWidget, ListThumbnail
from flask_appbuilder.models.group import aggregate_count, aggregate_sum, aggregate_avg, aggregate_count
from flask_appbuilder import action
from flask_appbuilder.filemanager import get_file_original_name



#
#class UploadComments(BaseView):
#    default_view = 'upload'
#    @expose('/upload', methods=('POST','GET'))
#    def upload(self):
#        return self.render_template('upload.html')


class CommentView(ModelView):
    datamodel = SQLAInterface(Comments)
    search_columns = ['included','closed', 'document','revision', 'reply']
    base_order = ('id_c','asc')
    order_columns = ['id_c']
    label_columns = {
        'pretty_style' : 'Type',
        'pretty_included': 'Included',
        'pretty_closed': 'Closed',
        'document': 'Bapco Code',
        'pretty_comment': 'Comments',
        'pretty_reply': 'Replies',
        'pretty_revision': 'Rev',
        'id_c': 'ID-C',
    }
    list_columns = ['document','id_c','partner','pretty_revision','page', 'author','pretty_style', 'pretty_comment', 'pretty_reply', 'pretty_included','pretty_closed']

    #list_widget = ListThumbnail
    
    add_exclude_columns = ['created_on', 'changed_on']
    edit_exclude_columns = ['created_on', 'changed_on']
    show_exclude_columns = ['comments']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

class CommentsChart(GroupByChartView):
    datamodel = SQLAInterface(Comments)
    chart_type = 'BarChart'
    definitions = [
       
        {
            'label': 'Author',
            'group': 'author',
            'series': [
                (aggregate_count, 'comment'),
                (aggregate_sum, 'closed'),
                (aggregate_sum, 'included')             
            ]
        },
        {
            'label': 'Document',
            'group': 'doc',
            'series': [
                (aggregate_count, 'comment'),
                (aggregate_sum, 'closed'),
                (aggregate_sum, 'included'),
                (aggregate_count, 'open_comments')             
            ]
        }
        ]

class CommentsPieChart(GroupByChartView):
    datamodel = SQLAInterface(Comments)
    chart_type = 'PieChart'
    definitions = [
       
        {
            'label': 'Closed',
            'group': 'closed',
            'series': [(aggregate_count, 'closed')]
        },
        {
            'label': 'Included',
            'group': 'included',
            'series': [(aggregate_count, 'included')]
        }
        ]

class RevisionView(ModelView):
    datamodel = SQLAInterface(Revisions)
    label_columns = {
        'pretty_revision': 'Rev.',
        'pretty_date': 'Date',
        'pretty_date_trs': 'TR Date'
    }
    list_columns = ['pretty_doc_revision', 'trasmittal', 'pretty_date_trs', 'note', 'file_name', 'download']
    add_exclude_columns = ['created_on', 'changed_on']
    edit_exclude_columns = ['created_on', 'changed_on']
    add_columns = ['file', 'revision', 'trasmittal', 'date_trs', 'note']
    show_exclude_columns = ['comments']

    related_views = [CommentView]

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

    def pre_add(self,item):
        item.document_id, item.partner = check_Doc(self, item)
        item.reply = check_reply(self, item)
        
        filename = get_file_original_name(item.file)
        

    def post_add(self, item):
        
        print('post add functions on revision')
        comments(item)


class DocumentView(ModelView):
    datamodel = SQLAInterface(Document)
    related_views = [CommentView, RevisionView]
    add_exclude_columns = ['created_on', 'changed_on','comments']
    edit_exclude_columns = ['created_on', 'changed_on','comments']
    show_exclude_columns = ['comments']
    search_exclude_columns = ['created_on', 'changed_on']
    #search_columns = ['name', 'partner' ]
    label_columns = {
        'name': 'Bapco Code',
        'count': 'Tot',
        'count_included': 'Included',
        'count_closed': 'Closed',
        'count_open': 'Open',
        'count_no_reply': "No Reply",
    }
    list_columns = ['name','partner', 'revision', 'count', 'count_open', 'count_no_reply', 'count_closed', 'count_included']
    
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

"""
    Application wide 404 error handler
"""

@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404




db.create_all()
from mass_update import mass_update


#appbuilder.add_view(UploadComments,'Upload Comments',icon="fa-folder-open-o", category="My Category", category_icon='fas fa-comment')
appbuilder.add_view(RevisionView,'Upload Comments',icon="fas fa-code-branch", category="Comments", category_icon='fas fa-comment')
appbuilder.add_view(DocumentView,'Document',icon="fas fa-file-pdf", category="Comments", category_icon='fas fa-comment')
appbuilder.add_view(CommentView,'Comments',icon="fas fa-comments", category="Comments", category_icon='fas fa-comment')
appbuilder.add_view(CommentsChart,'Comment Chart',icon="fas fa-code-branch", category="Statistics", category_icon='fas fa-comment')
appbuilder.add_view(CommentsPieChart,'Comment Pie Chart',icon="fas fa-code-branch", category="Statistics", category_icon='fas fa-comment')


#mass_update()