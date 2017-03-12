# from mezzanine.pages.models import Page

# def pre_order(request):
#     try:
#         #find current category page by url slug
#         page = Page.objects.filter(content_model='category').filter(slug = request.path[1:-1])
#         status = request.GET.get("pre_order", False)
#     except:
#         status = False
    
#     return {'status' : status}