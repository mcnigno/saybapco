from flask import render_template, redirect
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, IndexView, BaseView, expose, MasterDetailView, DirectByChartView, GroupByChartView
from app import appbuilder, db
from .models import Document, Comments, Revisions
from helpers import comments, check_Doc, check_reply, set_comments_blank, set_comments_included, report_all, check_doc_closed, check_doc_closed2
from flask_appbuilder.widgets import ListBlock, ListCarousel, ListMasterWidget, ListThumbnail
from flask_appbuilder.models.group import aggregate_count, aggregate_sum, aggregate_avg, aggregate_count
from flask_appbuilder import action, has_access
from flask_appbuilder.filemanager import get_file_original_name
from mass_update import transmittall
from flask import request, send_file
from config import UPLOAD_FOLDER
from flask_appbuilder.models.sqla.filters import FilterStartsWith, FilterEqualFunction, FilterEqual
from mass_update import test_closed


#
#class UploadComments(BaseView):
#    default_view = 'upload'
#    @expose('/upload', methods=('POST','GET'))
#    def upload(self):
#        return self.render_template('upload.html')
class Report(BaseView):
    @expose('/report/', methods=['POST', 'GET'])
    def report(self):
        print('report')
        #print(request.submit.value)
        if request.method == 'POST':
            print('post')
            print('POST', request.data) 
    
        return self.render_template('reports.html')
    
    @expose('/forward/', methods=['POST', 'GET'])
    def forward(self):
        print('forward')
        #print(request.submit.value)
        if request.method == 'POST':        
            print('forward')
            print('forward')
            ws = report_all()
            return send_file(ws, as_attachment=True)
        return self.render_template('reports.html')

class CommentView(ModelView):
    datamodel = SQLAInterface(Comments)
    search_columns = ['included','closed', 'document','revision','comment', 'reply']
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
        'pretty_partner': 'Partner',

        'id_c': 'ID-C',
    }
    #list_columns = ['document','id_c','pretty_partner','pretty_revision','page', 'author','pretty_style', 'pretty_comment', 'pretty_reply', 'pretty_included','pretty_closed']
    list_columns = ['document','pretty_revision','pretty_style', 'pretty_comment','note',  'pretty_reply', 'pretty_included','pretty_closed']

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
    @has_access
    @action("close", "Close", "Close all Really?", "fa-rocket")
    def close(self, items):
        if isinstance(items, list):
            for item in items:
                item.closed = True
                self.datamodel.edit(item)
            self.update_redirect()
        else:
            items.closed = True
            self.datamodel.edit(item)
        return redirect(self.get_redirect())
    def post_update(self, item):
        check_doc_closed(item.document_id)

'''
class OpenCommentsView(ModelView):
    datamodel = SQLAInterface(Comments)

    base_filters = [['type_reply', FilterEqual, True],
                    ['closed', FilterEqual, False]
    
    ]
'''

class CommentsChart(GroupByChartView):
    datamodel = SQLAInterface(Comments)
    chart_type = 'BarChart'
    height = '2000px'
    chart_title = 'Open CS Chart'
    search_columns = ['type_reply', 'included', 'closed','style']
    base_filters = [['type_reply', FilterEqual, True],
                    ['closed', FilterEqual, False]
    
    ]
    definitions = [
       
        {
            'label': 'Author',
            'group': 'author',
            'series': [
                (aggregate_count, 'comment'),
                (aggregate_sum, 'closed'),
                #(aggregate_sum, 'included')             
            ]
        },
        {
            'label': 'Document',
            'group': 'doc',
            'series': [
                #(aggregate_count, 'comment'),
                #(aggregate_sum, 'closed'),
                #(aggregate_sum, 'included'),
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
        'pretty_doc_revision': 'Document',
        'pretty_date': 'Date',
        'pretty_date_trs': 'Trans. Date',
        'trasmittal': 'Transmittal'
    }
    list_columns = ['pretty_doc_revision', 'pretty_revision', 'trasmittal', 'pretty_date_trs', 'note', 'file_name', 'download']
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
        check_doc_closed(item.document_id)



class DocumentView(ModelView):
    datamodel = SQLAInterface(Document)
    related_views = [CommentView, RevisionView]
    add_exclude_columns = ['created_on', 'changed_on','comments']
    edit_exclude_columns = ['created_on', 'changed_on','comments']
    show_exclude_columns = ['comments']
    search_exclude_columns = ['created_on', 'changed_on']
    search_columns = ['partner', 'serial','closed' ]
    label_columns = {
        'name': 'Bapco Code',
        'count': 'Tot',
        'count_included': 'Included',
        'count_closed': 'Closed',
        'count_open': 'Open',
        'count_no_reply': "No Reply",
    }
    list_columns = ['name','partner', 'revision', 'count','is_closed','closed', 'count_open', 'count_no_reply', 'count_closed', 'count_included']
    
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

    @action("check", "Check", "Check all Really?", "fa-rocket")
    def check(self, items):
        if isinstance(items, list):
            for item in items:
                test_closed(item.id)
            self.update_redirect()
        else:
            test_closed(items.id)
        return redirect(self.get_redirect())

"""
    Application wide 404 error handler
"""

@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404##




db.create_all()
from mass_update import mass_update
appbuilder.security_cleanup()

#appbuilder.add_view(UploadComments,'Upload Comments',icon="fa-folder-open-o", category="My Category", category_icon='fas fa-comment')
#appbuilder.add_view(Report,'Reports',icon="fa-folder-open-o", category="My Category", category_icon='fas fa-comment')

appbuilder.add_view(RevisionView,'Upload Comments',icon="fas fa-code-branch", category="Comments", category_icon='fas fa-comment')
appbuilder.add_view(DocumentView,'Document',icon="fas fa-file-pdf", category="Comments", category_icon='fas fa-comment')
appbuilder.add_view(CommentView,'Comments',icon="fas fa-comments", category="Comments", category_icon='fas fa-comment')
appbuilder.add_view(CommentsChart,'Comment Chart',icon="fas fa-code-branch", category="Statistics", category_icon='fas fa-comment')
appbuilder.add_view(CommentsPieChart,'Comment Pie Chart',icon="fas fa-code-branch", category="Statistics", category_icon='fas fa-comment')
appbuilder.add_view_no_menu(Report)

#mass_update()
#set_comments_blank()
#set_comments_included()
transmittall()


#check_doc_closed2() 
