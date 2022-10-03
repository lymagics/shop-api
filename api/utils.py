def paginated_response(data, pagination, status_code=200, headers=None):
    """Prepare response for pagination schema."""
    return {
        "data": data,
        "pagination": pagination
    }, status_code, headers


def checkout_response(url: str):
    """Prepare response for checkout schema."""
    return {
        "url": url
    }
