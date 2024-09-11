def update_product_rating(product):
    """Update the rating of the given product based on its comments."""

    comments = product.comments.all()
    count = len(comments)

    if count == 0:
        return
    total_rating = sum(comment.rating for comment in comments)
    product.rating = total_rating / count