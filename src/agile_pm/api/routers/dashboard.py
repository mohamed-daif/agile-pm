"""Simple health dashboard."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard"])

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Agile-PM Status</title>
    <style>
        body { font-family: system-ui; max-width: 800px; margin: 40px auto; padding: 20px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .healthy { background: #d4edda; color: #155724; }
        .unhealthy { background: #f8d7da; color: #721c24; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>🚀 Agile-PM Dashboard</h1>
    <div id="status">Loading...</div>
    <script>
        fetch('/api/v1/system/health')
            .then(r => r.json())
            .then(data => {
                document.getElementById('status').innerHTML = 
                    '<div class="status ' + (data.status === 'healthy' ? 'healthy' : 'unhealthy') + '">' +
                    '<strong>Status:</strong> ' + data.status + '</div>';
            });
    </script>
</body>
</html>
"""

@router.get("/", response_class=HTMLResponse)
async def dashboard():
    """Health dashboard."""
    return DASHBOARD_HTML
