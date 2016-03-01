"""
This module holds generalized base view classes inspired by Django's Class
Based Views.
"""
from flask import abort, render_template, request, redirect, url_for
from flask.views import View, MethodView
from sqlalchemy import or_

from core import Exception


class ContextMixin(object):
    def get_context(self, **kwargs):
        """
        Puts together the context.
        """
        return kwargs


class TemplateResponseMixin(object):
    template = None

    def get_template(self):
        """
        Returns the template defined on the class.
        """
        return self.template

    def render_template(self, **kwargs):
        """
        Call Flask's render template method.
        """
        return render_template(self.get_template(), **kwargs)


class TemplateView(TemplateResponseMixin, ContextMixin, View):
    """
    Base view class.
    """
    def dispatch_request(self, *args, **kwargs):
        context = self.get_context(**kwargs)
        return self.render_template(**context)


class FormMixin(ContextMixin):
    """
    Designed to be used with WTForms.
    """
    success_url = None
    form_class = None
    csrf_protection = True
    initial = {}

    def get_initial(self):
        """
        Returns the default values to initialize the form with.
        """
        return self.initial.copy()

    def get_form_args(self):
        """
        Gather the submitted arguments from request POST data.
        """
        form_args = request.form
        return (form_args,)

    def get_form_class(self):
        if not self.form_class:
            raise Exception("No Form class specified")

        return self.form_class

    def get_form(self, form_class=None):
        if hasattr(self, '_form'):
            # returned cached form on instance of view.
            return self._form

        if not form_class:
            form_class = self.get_form_class()

        self._form = form_class(*self.get_form_args(), csrf_enabled=self.csrf_protection, **self.get_initial())
        return self._form

    def get_success_url(self, **kwargs):
        """
        Success url is where the user will be redirected to upon successful
        form submission.
        """
        if not self.success_url:
            raise Exception('Must specify a success url')

        return url_for(self.success_url, **kwargs)

    def form_valid(self, form):
        """
        This is where things can be down when form is valid.
        """
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        """
        Return to the view the invalid form.
        """
        return self.render_template(**self.get_context(form=form))

    def get_context(self, **kwargs):
        """
        Add the form to the context.
        """
        kwargs.setdefault('form', self.get_form())
        return super(FormMixin, self).get_context(**kwargs)


class ProcessFormView(MethodView):
    """
    A mixin that renders the Form no GET and processes it on POST.
    """
    def get(self):
        return self.render_template(**self.get_context())

    def post(self):
        """
        Process the form.
        """
        form = self.get_form()
        if form.validate():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def put(self):
        return self.post()


class BaseFormView(FormMixin, ProcessFormView):
    """
    View to handle Forms.
    """


class FormView(TemplateResponseMixin, BaseFormView):
    """
    Displays the form and renders a template respone.
    """


class MultipleObjectMixin(ContextMixin):
    """
    Mixin for list views. Pagination is based on SQLAlchemy's paginate
    """
    queryset = None
    service = None
    paginate = False
    paginate_by = 25
    page_kwarg = 'p'
    ordering = None
    joins = []
    context_object_name = 'items'

    def build_queryset(self, **kwargs):
        """
        The return value must be an instance of SQLAlchemy query object.

        Further filtering and queryset manipulation can be done in subclasses.
        """
        if self.queryset is not None:
            queryset = self.queryset
        elif self.service is not None:
            queryset = self.service.find()
        else:
            raise Exception(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )

        for j in self.joins:
            queryset = queryset.join(j)

        return queryset

    def get_queryset(self, **kwargs):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        SQLAlchemy query object.
        """
        queryset = self.build_queryset(**kwargs)
        queryset = self.order(queryset)

        return queryset

    def get_ordering(self):
        """
        Return the columns to order by.
        @return Iterable of SQLAlchemy column objects.
        """
        return self.ordering

    def order(self, queryset):
        """
        Order the queryset by set orderings.
        """
        ordering = self.get_ordering()
        if ordering:
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_paginate_by(self):
        """
        Get the number of items per page.
        """
        return self.paginate_by

    def get_context_object_name(self, object_list):
        """
        Get the name to use in the context.
        """
        if self.context_object_name:
            return self.context_object_name
        elif hasattr(object_list, '__model__'):
            return '{}_list'.format(object_list.__model__.__class__.__name__.lower())
        else:
            return None

    def paginate_queryset(self, queryset, page_size):
        """
        Return the sqlalchemy paginate object.
        """
        page = request.args.get(self.page_kwarg, 1)
        try:
            page = int(page)
        except ValueError:
            abort(404)

        return queryset.paginate(page, per_page=25)

    def get_context(self, **kwargs):
        """
        Add paginated query object to context.
        """
        page_size = self.get_paginate_by()
        context_object_name = self.get_context_object_name(self.service)
        if self.paginate:
            queryset = self.paginate_queryset(self.get_queryset(**kwargs), page_size)
        else:
            queryset = self.get_queryset(**kwargs)

        context = {context_object_name: queryset}
        context.update(kwargs)

        return super(MultipleObjectMixin, self).get_context(**context)


class BaseListView(MultipleObjectMixin, View):
    """
    A base view for displaying a list of objects.
    """


class ListView(TemplateResponseMixin, BaseListView):
    """
    List view for objects.
    """
    def dispatch_request(self, *args, **kwargs):
        context = self.get_context(**kwargs)
        return self.render_template(**context)


class FilteredListView(FormMixin, ListView):
    """
    A List view that has a filter form that allows for manipulating the query
    for the list of objects.

    The Form can only have SelectField or QuerySelectField or StringField or
    DateField types.

    If DateField types are used, its expected that two are present and named
    'start' and 'end'. These will create query statements that restrict the
    datetime column in column_lookup to be between the two.
    """
    column_lookup = {}

    def get_form_args(self):
        """
        Gather the submitted arguments from request GET data.
        """
        form_args = request.args
        return (form_args,)

    def filtered_queryset(self, queryset, form):
        """
        Return the queryset, filtered by form variables.

        @param queryset SQLAlchemy queryset
        @param form WTForm Form
        @param SQLAlchemy queryset
        """
        filters = []

        for field in form:
            column = self.column_lookup.get(field.short_name, None)
            val = field.data

            if not val:
                # Skip if val is not defined
                continue

            if field.type == "StringField":
                # Handle string search. String search is a little different in
                # that you can specify mulitple columns in the column_lookup
                # variable to the form field name.

                if hasattr(column, '__iter__'):
                    # If 'column' is iterable, then create an or_ with all of
                    # them.
                    ors = []
                    for col in column:
                        ors.append(col.ilike(u"%{}%".format(val)))

                    filters.append(or_(*ors))
                else:
                    filters.append(column.ilike(u"%{}%".format(val)))

            elif field.type == "DateField":
                # Handle date range search. Expecting field name to be either
                # 'start' or 'end'. One or both can be specified.
                if field.short_name == 'start':
                    filters.append(column >= val)
                elif field.short_name == 'end':
                    filters.append(column <= val)
                else:
                    raise Exception("Unexpectected DateField name: {}.".format(field.short_name))
            else:
                if val and column:
                    filters.append((column == val))

        return queryset.filter(*filters)

    def build_queryset(self, **kwargs):
        """
        Use the form values to filter the queryset.
        """
        form = self.get_form()
        qs = super(FilteredListView, self).build_queryset(**kwargs)

        if form.validate():
            # Filter the queryset with form arguments
            qs = self.filtered_queryset(qs, form)

        return qs
