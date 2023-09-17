from typing import Any, Optional
from django import http
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.http import FileResponse
from course_drapeau.forms.account import DriverForm, RunnerForm, UserTypeForm

from course_drapeau.permissions import is_member
from .base import CustomTemplateView
import logging

logger = logging.getLogger(__name__)


class IndexView(CustomTemplateView):
    template_name = 'course_drapeau/pages/index.html'


class AboutView(CustomTemplateView):
    template_name = 'course_drapeau/pages/about.html'
    items = [
        ('question1', 'answer1'),
        ('question2', 'answer2'),
        ('question3', 'answer3'),
        ('question4', 'answer4'),
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.items
        return context


class ContactView(CustomTemplateView):
    template_name = 'course_drapeau/pages/contact.html'


class TronconsView(CustomTemplateView):
    template_name = 'course_drapeau/pages/route.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GPX_traces'] = Section.objects.all()
        return context


class SuiviView(CustomTemplateView):
    template_name = 'course_drapeau/pages/tracking.html'


class Card:
    def __init__(self, title, id, template):
        self.title = title
        self.id = id
        self.template = f"course_drapeau/pages/account/cards/{template}.html"


class AccountView(UserPassesTestMixin, CustomTemplateView):
    template_name = 'course_drapeau/pages/account/index.html'
    cards = [[
        Card("Mes informations personnelles", "info", "info"),
        # Card("Mon certificat médical", "certif", "certif"),
        # Card("Paiement de la course", "payement", "payement")],
        # [
        # Card("Logistique", "logistique", "logistique"),
        # Card("Liste d'affaires à emmener",
        #      "affaires", "affaires"),
        # Card("Hébergement", "hebergement", "hebergement")],
        # [
        # Card("Mes tronçons", "troncons", "troncons"),
        # Card("Mon trinôme", "trinomes", "trinomes")]]
    ]]

    def test_func(self):
        return is_member(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cards'] = self.cards
        return context


class FileView(DetailView):
    # queryset = File.objects.all()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        as_attachment = bool(request.GET.get('download', False))
        response = FileResponse(instance.upload, as_attachment=as_attachment)
        return response


class RegisterView(CustomTemplateView):
    template_name = 'course_drapeau/pages/register.html'

    def post(self, request, *args, **kwargs):

        user_type_form = UserTypeForm(request.POST)
        driver_form = DriverForm(request.POST)
        runner_form = RunnerForm(request.POST)
        user = request.user
        error_response = self.render_to_response(self.get_context_data(
            user_type_form=user_type_form,
            driver_form=driver_form,
            runner_form=runner_form
        ))
        if not user.is_authenticated:
            return error_response
        if user_type_form.is_valid():
            user_type = user_type_form.cleaned_data['user_type']
            if user_type == 'driver' and driver_form.is_valid():
                driver = driver_form.save(commit=False)
                driver.user = user
                driver.save()
                return redirect('account')
            elif user_type == 'runner' and runner_form.is_valid():
                runner = runner_form.save(commit=False)
                runner.user = user
                runner.save()
                if runner.save_group(runner_form.cleaned_data['group_member_choice']):
                    return redirect('account')
                else:
                    pass
                    # TODO
        return error_response

    def get(self, request, *args, **kwargs):
        if is_member(request.user):
            return redirect('account')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type_form'] = kwargs.get(
            'user_type_form', UserTypeForm())
        context['driver_form'] = kwargs.get('driver_form', DriverForm())
        context['runner_form'] = kwargs.get('runner_form', RunnerForm())
        return context