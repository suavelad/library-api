from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status,filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from . import models, serializers

from library.utils import ViewsetMixin,success_20X,error_400,serializer_errors


from recommendation.engine import recommend_books
# Create your views here.
class BookViewSet(ViewsetMixin, ModelViewSet):
    queryset = models.Book.objects.all()
    serializer_class = serializers.BooksSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post','get','put','delete']


    # Add search filter backend
    filter_backends = [filters.SearchFilter]
    
    # Define which fields are searchable
    search_fields = ['title','author__first_name','author__last_name']  



    def get_permissions(self):
        """
        Override to apply different permissions for different actions.
        """
        if self.action in ['create', 'update', 'destroy']:
            # Require authentication for these actions
            return [IsAuthenticated()]
        return [AllowAny()]  # Allow any user for other actions

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        
        return Response(serializer.data)

    def create (self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)

        return success_20X("book created successfilly",status.HTTP_201_CREATED)


   
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(serializers.BooksSerializer(instance).data)
    

   
    def destroy(self,request, *args, **kwargs):
        instance = self.get_object()
        instance.archive()
        return Response(data='delete success')
    


    @action(detail=False, methods=['post'],serializer_class=serializers.FavoriteSerializer)
    def add_favorite(self, request):

        serializer = serializers.FavoriteSerializer(data=request.data, partial=True)
        if serializer.is_valid():
        
            book_id = serializer.validated_data["book_id"]
            user = request.user
            try:
                book = models.Book.objects.get(id=book_id)
                if models.Favorite.objects.filter(user=user, book=book).exists():
                    return Response({'detail': 'Book is already in favorites'}, status=status.HTTP_400_BAD_REQUEST)
                models.Favorite.objects.create(user=user, book=book)
            except models.Book.DoesNotExist:
                return Response({'detail': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

            # Call the recommendation system here after adding a favorite
            recommendations = self.get_recommendations(user) 
    
            # recommendations = recommend_books(book.title) // using the recommendation engine

            return Response({
                'detail': 'Book added to favorites',
                'recommendations': recommendations
            }, status=status.HTTP_200_OK)
        
        error_message = serializer_errors(serializer.errors)
        return error_400(error_message)

    
    @action(detail=False, methods=['post'],serializer_class=serializers.FavoriteSerializer)
    def remove_favorite(self, request):
        book_id = request.data.get('book_id')
        user = request.user
        try:
            book = models.Book.objects.get(id=book_id)
            models.Favorite.objects.filter(user=user, book=book).delete()
        except models.Book.DoesNotExist:
            return Response({'detail': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'detail': 'Book removed from favorites'}, status=status.HTTP_200_OK)

    def get_recommendations(self, user):
        favorite_books = user.favorites.values_list('book', flat=True)
        if not favorite_books:
            return []
        
        genres = models.Book.objects.filter(id__in=favorite_books).values_list('genre', flat=True)
        keywords = models.Book.objects.filter(id__in=favorite_books).values_list('keywords', flat=True)

        similar_books = models.Book.objects.filter(
            models.Q(genre__in=genres) | models.Q(keywords__in=keywords)
        ).exclude(id__in=favorite_books).distinct()[:5]  # Get 5 recommendations

        return serializers.BooksSerializer(similar_books, many=True).data

        


class AuthorViewSet(ViewsetMixin, ModelViewSet):
    queryset = models.Author.objects.all()
    serializer_class = serializers.AuthorsSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post','get','put','delete']

    def get_permissions(self):
        """
        Override to apply different permissions for different actions.
        """
        if self.action in ['create', 'update','partial', 'destroy']:
            # Require authentication for these actions
            return [IsAuthenticated()]
        return [AllowAny()]  # Allow any user for other actions
    

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(serializer.data)


    def create (self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)

        return success_20X("author created successfilly",status.HTTP_201_CREATED)


   
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(serializers.BooksSerializer(instance).data)
    

    
    def destroy(self,request, *args, **kwargs):
        instance = self.get_object()
        instance.archive()
        return Response(data='deleted successful')
        
        

