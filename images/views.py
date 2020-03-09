import redis
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from actions.utils import create_action
from common.decorators import ajax_required
from images.forms import ImageCreateForm
from images.models import Image

r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)


@login_required
def image_create(request):
    """
        View for creating an Imge using th Javascript Bookmarklet.
    """
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_item = form.save(commit=False)

            new_item.user = request.user
            new_item.save()
            messages.success(request, 'Image added successfully')
            return redirect(new_item.get_absolute_url())
    else:
        form = ImageCreateForm(data=request.GET)
    return render(request=request, template_name='images/image/create.html', context={'section': 'images',
                                                                                      'form': form})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # increment total image views by 1
    total_views = r.incr(f'image:{image.id}:views')
    # increment image ranking by 1
    r.zincrby('image_ranking', image.id, 1)
    return render(request=request, template_name='images/image/detail.html', context={'section': 'images',
                                                                                      'image': image,
                                                                                      'total_views': total_views,
                                                                                      })


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'ko'})


@login_required
def image_list(request):
    print('page = ', request.GET.get('page'))
    images = Image.objects.all().order_by('id')
    paginator = Paginator(images, 3)
    page = request.GET.get('page')
    if page is None:
        page = 1
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        print('sjsjsij')
        images = paginator.page(1)
    except EmptyPage:
        print('EmptyPage')
        if request.is_ajax():
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        print('aaaaa')
        return render(request, template_name='images/image/list_ajax.html',
                      context={'section': 'images', 'images': images})
    return render(request, template_name='images/image/list.html', context={'images': images})


@login_required
def image_ranking(request):
    # get image ranking dictionary
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    # get most viewed images
    most_viewed = list(Image.objects.filter(
        id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request,
                  'images/image/ranking.html',
                  {'section': 'images',
                   'most_viewed': most_viewed})
