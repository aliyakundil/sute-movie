from django.shortcuts import render
from .models import Movie, Category, IpModel, timezone
from .forms import MovieForm, UserRegisterForm, UserLoginForm
from django.shortcuts import render, get_object_or_404, redirect
import json
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth import login, logout
from rest_framework import viewsets
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import ListView, DetailView
from django.http import JsonResponse

def index(request):
    post = Movie.objects.all()
    category2 = Category.objects.all()
    common_tags = Movie.tags.most_common()[:3]

    return render(request, 'main/index.html', {'post':post, 'category2':category2, 'common_tags':common_tags})


def movie_detail(request, slug):
    post = Movie.objects.get(slug=slug)

    msg = False

    if request.user.is_authenticated:
        user = request.user

        if post.likes.filter(id=user.id).exists():
            msg = True


    return render(request, 'main/blog_detail.html',
                  {'post': post, 'msg': msg})


def like_post(request):
    data = json.loads(request.body)
    id = data["id"]
    post = Movie.objects.get(id=id)
    checker = None

    if request.user.is_authenticated:

        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            checker = 0


        else:
            post.likes.add(request.user)
            checker = 1

    likes = post.likes.count()

    info = {
        "check": checker,
        "num_of_likes": likes
    }

    return JsonResponse(info, safe=False)

def index(request):
    post = Movie.objects.all()
    category2 = Category.objects.all
    # common_tags = Movie.tags.most_common()[:4]

    return render(request, 'main/index.html', {'post':post, 'category2':category2,
                                               # 'common_tags':common_tags
                                               })

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def post_detail(request, pk):
    # post = get_object_or_404(Post, pk=pk)
    post = Movie.objects.get(pk=pk)
    ip = get_client_ip(request)
    msg = False
    if request.user.is_authenticated:
        user = request.user

        if post.likes.filter(id=user.id).exists():
            msg = True


    if IpModel.objects.filter(ip=ip).exists():
        post.views.add(IpModel.objects.get(ip=ip))
    else:
        IpModel.objects.create(ip=ip)
        post.views.add(IpModel.objects.get(ip=ip))
    return render(request, 'main/post_detail.html', {'post': post, 'msg':msg})

def post_new(request):
    form = MovieForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        # post.author = request.user
        post.published_date = timezone.now()
        try:
            post.image = request.FILES['image']
        except:
            post.image = post.image
        post.save()
        return redirect('/', pk=post.pk)
    else:
        form = MovieForm()
    return render(request, 'main/post_new.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        form = MovieForm(request.POST, instance=post)
        if form.is_valid():
            post.title = request.POST['title']
            post.text = request.POST['text']
            post.author = request.user
            post.published_date = timezone.now()
            try:
                post.image = request.FILES['image']
            except:
                post.image = post.image

            post.save()
            return redirect('/', pk=post.pk)
    else:
        form = MovieForm(instance=post)
    return render(request, 'main/post_edit.html', {'form': form})

def post_delete(request, pk):
    news = Movie.objects.get(pk=pk)
    news.delete()
    return redirect('/')

def filter(request, pk):
    post = Movie.objects.all()
    if pk == 1:
        now = datetime.now() - timedelta(minutes=60*24*7)
        post = post.filter(created_date__gte=now)
    elif pk == 2:
        now = datetime.now() - timedelta(days=30)
        post = post.filter(created_date__lte=now)
    elif pk == 3:
        post = post

    return render(request, 'main/filter.html', {'post':post})



def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'login user')
            return redirect('/')
        else:
            messages.error(request, 'Error login')
    else:
        form = UserLoginForm()
    return render(request, 'register/login.html', {'form':form})

def user_logout(request):
    logout(request)
    return redirect('index')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Register Success')
            return redirect('/')
        else:
            messages.error(request, 'Register Error')
    else:
        form = UserRegisterForm()
    return render(request, 'register/register.html', {'form':form})

def show_category(request, pk):
    post = Movie.objects.filter(pk=pk)
    all_category = Category.objects.all()
    return render(request, 'main/show_category.html', {
        'all_category' : all_category,
        'post':post
    })


class PostViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filter_fields = ['text']
    search_fields = ['author', 'title']
    ordering_fields = ['author', 'text']
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthenticated]

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
        serializer.save()

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class IndexView(ListView):

    model = Movie
    template_name = "main/scroll.html"
    context_object_name = 'all_news'
    paginate_by = 2


class PostDetailView(DetailView):
    model = Movie
    context_object_name = 'blog'
    template_name = 'blog-detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        # adding like count
        like_status = False
        ip = get_client_ip(request)
        if self.object.likes.filter(id=IpModel.objects.get(ip=ip).id).exists():
            like_status = True
        else:
            like_status = False
        context['like_status'] = like_status

        return self.render_to_response(context)
