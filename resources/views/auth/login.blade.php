<!doctype html>
<html lang="id">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Masuk admin — GIS Puskesmas</title></head>
<body>
<main>
    <h1>Masuk admin</h1>
    @if ($errors->any())<p role="alert">Email atau kata sandi tidak valid. Silakan coba lagi.</p>@endif
    <form method="post" action="{{ route('admin.login') }}">
        @csrf
        <p><label for="email">Email</label><input id="email" name="email" type="email" value="{{ old('email') }}" autocomplete="username" required maxlength="254"></p>
        <p><label for="password">Kata sandi</label><input id="password" name="password" type="password" autocomplete="current-password" required maxlength="72"></p>
        <button type="submit">Masuk</button>
    </form>
    <a href="/">Kembali ke peta publik</a>
</main>
</body>
</html>
