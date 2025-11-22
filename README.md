# Smarter OS API

FastAPI service for unified contact form submissions across smarterbot.cl and smarterbot.store.

## Features

- ✅ POST `/contact` - Submit contact form
- ✅ GET `/contacts` - List recent contacts
- ✅ GET `/health` - Health check
- ✅ CORS configured for all Smarter OS domains
- ✅ Supabase integration for data persistence
- ✅ Resend integration for email notifications
- ✅ Automatic OpenAPI documentation at `/docs`

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE=eyJ...
RESEND_API_KEY=re_...
RESEND_FROM=no-reply@smarterbot.cl
ADMIN_EMAIL=smarterbotcl@gmail.com
EOF

# Run server
uvicorn main:app --reload --port 8000
```

### Docker

```bash
# Build image
docker build -t api.smarterbot.cl .

# Run container
docker run -d \
  -p 8000:8000 \
  -e SUPABASE_URL=https://your-project.supabase.co \
  -e SUPABASE_SERVICE_ROLE=eyJ... \
  -e RESEND_API_KEY=re_... \
  -e RESEND_FROM=no-reply@smarterbot.cl \
  -e ADMIN_EMAIL=smarterbotcl@gmail.com \
  --name api-smarterbot \
  api.smarterbot.cl
```

### Docker Compose

Add to `dkcompose/docker-compose.yml`:

```yaml
services:
  api-smarterbot:
    build: ../api.smarterbot.cl
    container_name: api-smarterbot
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE=${SUPABASE_SERVICE_ROLE}
      - RESEND_API_KEY=${RESEND_API_KEY}
      - RESEND_FROM=${RESEND_FROM:-no-reply@smarterbot.cl}
      - ADMIN_EMAIL=${ADMIN_EMAIL:-smarterbotcl@gmail.com}
    networks:
      - smarteros
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api-smarterbot.rule=Host(`api.smarterbot.cl`)"
      - "traefik.http.routers.api-smarterbot.entrypoints=websecure"
      - "traefik.http.routers.api-smarterbot.tls=true"
      - "traefik.http.routers.api-smarterbot.tls.certresolver=letsencrypt"
      - "traefik.http.services.api-smarterbot.loadbalancer.server.port=8000"
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Usage

### Submit Contact Form

```bash
curl -X POST http://localhost:8000/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "message": "Hola, quiero más información sobre automatización",
    "phone": "+56912345678",
    "source": "smarterbot.cl"
  }'
```

Response:
```json
{
  "ok": true,
  "message": "Contact submitted successfully"
}
```

### List Contacts

```bash
curl http://localhost:8000/contacts?limit=5&status=new
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | ✅ | - | Supabase project URL |
| `SUPABASE_SERVICE_ROLE` | ✅ | - | Supabase service role key (bypasses RLS) |
| `RESEND_API_KEY` | ⚠️ | - | Resend API key (optional, but email won't work without it) |
| `RESEND_FROM` | ❌ | `no-reply@smarterbot.cl` | From email address |
| `ADMIN_EMAIL` | ❌ | `smarterbotcl@gmail.com` | Admin notification email |

## Integration

Update frontend forms to use the new API:

**smarterbot.cl/components/contact-section.tsx**:
```typescript
const res = await fetch("https://api.smarterbot.cl/contact", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name,
    email,
    message,
    phone,
    source: "smarterbot.cl",
  }),
})
```

**smarterbot.store/src/pages/Contact.tsx**:
```typescript
const res = await fetch("https://api.smarterbot.cl/contact", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name,
    email,
    message,
    phone,
    source: "smarterbot.store",
  }),
})
```

## Database Schema

Requires `contacts` table in Supabase:

```sql
create table public.contacts (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  email text not null,
  message text not null,
  phone text,
  source text,
  domain text,
  status text default 'new',
  created_at timestamp with time zone default now()
);

-- RLS (service role bypasses this)
alter table public.contacts enable row level security;
```

## Production Deployment

1. **Build and push to registry**:
```bash
docker build -t registry.smarterbot.cl/api:latest .
docker push registry.smarterbot.cl/api:latest
```

2. **Deploy with docker-compose** in production server

3. **Configure Traefik** for HTTPS (labels already included)

4. **Test endpoint**:
```bash
curl https://api.smarterbot.cl/health
```

## License

Part of Smarter OS ecosystem.
