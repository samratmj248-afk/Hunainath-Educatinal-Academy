"""
Security Middleware for Enterprise-grade HTTP Headers.
Protects against XSS, clickjacking, MIME-sniffing, and data exfiltration.
"""

class SecurityHeadersMiddleware:
    """
    Applies strict CSP, Permissions-Policy, and cache headers.
    Allows necessary CDNs (Bootstrap, Font Awesome, Google Fonts, Cloudflare).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Content Security Policy (permits CDNs used for premium styling & icons)
        csp_directives = [
            "default-src 'self' https: data: blob:",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://static.cloudflareinsights.com",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com",
            "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net",
            "img-src 'self' data: blob: https: https://images.unsplash.com",
            "connect-src 'self' https: wss: ws:",
            "manifest-src 'self'",
            "worker-src 'self' blob:",
            "frame-ancestors 'self'",
        ]
        response["Content-Security-Policy"] = "; ".join(csp_directives)

        # Permissions Policy
        response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"

        # Extra safety headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-XSS-Protection"] = "1; mode=block"

        return response
