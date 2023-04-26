from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy 
  
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin  #for user restrictions
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task

# Create your views here.


#login view
class CustomLoginView(LoginView):
    template_name = 'ToDo/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')
    


#registration view
class RegisterPage(FormView):
    template_name = 'ToDo/register.html'
    form_class = UserCreationForm
    redirect_authenticated_users = True
    success_url = reverse_lazy('tasks')


    #redirect user
    def form_valid(self, form):
        user = form.save()

        if user is not None:
            login(self.request, user)
            
        return super(RegisterPage, self).form_valid(form)
    

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        
        return super(RegisterPage, self).get(*args, **kwargs)



#list view
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'


    # filter http response by username 
    # restrict access to other users' data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)

        # count number of incomplete tasks
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''

        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__startswith=search_input)

            context['search_input'] = search_input
        return context


# detail view
class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task    
    context_object_name = 'task'
    template_name = 'ToDo/task.html'


#create view
class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')
    

    # set default user to logged in user
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)



#update view
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task    
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')


#task delete view
class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task #Task model 
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
