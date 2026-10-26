<!doctype html>
<html lang="id">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Admin — GIS Puskesmas</title></head>
<body><main>
    <h1>Admin</h1>
    <p>Anda masuk sebagai {{ auth()->user()->name }}.</p>
    <form method="post" action="{{ route('admin.logout') }}">@csrf<button type="submit">Keluar</button></form>
    <a href="/">Lihat peta publik</a>
</main></body>
</html>
