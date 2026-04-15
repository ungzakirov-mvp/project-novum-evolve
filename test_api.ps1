# Тестирование API на русском языке

Write-Host "=== Тест 1: Регистрация нового пользователя ===" -ForegroundColor Cyan
$response1 = Invoke-RestMethod -Uri "http://localhost:8000/auth/register" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"email": "user1@test.com", "password": "pass123"}'
Write-Host "Успешно! ID: $($response1.id), Email: $($response1.email)" -ForegroundColor Green

Write-Host "`n=== Тест 2: Попытка создать дубликат (должна быть ошибка на русском) ===" -ForegroundColor Cyan
try {
    Invoke-RestMethod -Uri "http://localhost:8000/auth/register" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"email": "user1@test.com", "password": "pass456"}'
} catch {
    $errorDetail = ($_.ErrorDetails.Message | ConvertFrom-Json).detail
    Write-Host "Ожидаемая ошибка: $errorDetail" -ForegroundColor Yellow
}

Write-Host "`n=== Тест 3: Вход с правильным паролем ===" -ForegroundColor Cyan
$response3 = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"email": "user1@test.com", "password": "pass123"}'
Write-Host "Успешный вход! ID: $($response3.id), Email: $($response3.email)" -ForegroundColor Green

Write-Host "`n=== Тест 4: Вход с неправильным паролем (должна быть ошибка на русском) ===" -ForegroundColor Cyan
try {
    Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"email": "user1@test.com", "password": "wrongpass"}'
} catch {
    $errorDetail = ($_.ErrorDetails.Message | ConvertFrom-Json).detail
    Write-Host "Ожидаемая ошибка: $errorDetail" -ForegroundColor Yellow
}

Write-Host "`n=== Тест 5: Вход с несуществующим email (должна быть ошибка на русском) ===" -ForegroundColor Cyan
try {
    Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"email": "nouser@test.com", "password": "pass123"}'
} catch {
    $errorDetail = ($_.ErrorDetails.Message | ConvertFrom-Json).detail
    Write-Host "Ожидаемая ошибка: $errorDetail" -ForegroundColor Yellow
}

Write-Host "`n=== Тест 6: Проверка здоровья ===" -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "http://localhost:8000/" -Method GET
$statusKey = $health.PSObject.Properties.Name[0]
Write-Host "Статус: $($health.$statusKey)" -ForegroundColor Green

Write-Host "`n✅ Все тесты выполнены!" -ForegroundColor Green
