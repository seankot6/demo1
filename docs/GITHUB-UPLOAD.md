# Как выложить инструкцию на GitHub

## 1. Создай репозиторий на сайте

1. Зайди на [github.com](https://github.com) → **New repository**
2. Имя, например: `chitaygorod-de-v1`
3. **Public** или Private
4. **Не** ставь галочки README / .gitignore (они уже в папке)
5. **Create repository**

## 2. Загрузи с компьютера (PowerShell)

Открой терминал в папке проекта:

```powershell
cd "C:\Users\Пользователь\Desktop\redexpert"

git init
git add README.md .gitignore docs/
git add gen_fill_sql.py gen_full_sql.py _gen_sql.py
git commit -m "Добавить инструкции ДЭ В1: модуль 1 и модуль 2 с кодом WPF"

git branch -M main
git remote add origin https://github.com/ТВОЙ_ЛОГИН/chitaygorod-de-v1.git
git push -u origin main
```

Замени `ТВОЙ_ЛОГИН` и имя репозитория на свои.

## 3. Если просит логин

- Используй **Personal Access Token** вместо пароля:  
  GitHub → Settings → Developer settings → Personal access tokens → Generate
- Или установи [GitHub Desktop](https://desktop.github.com/) и сделай **Publish repository**

## 4. Что попадёт в репозиторий

| Файл | Назначение |
|------|------------|
| `README.md` | Оглавление |
| `docs/module-01-database.md` | Модуль 1 |
| `docs/module-02-wpf-app.md` | Модуль 2 + весь код |
| `docs/GITHUB-UPLOAD.md` | Эта инструкция |
| `gen_*.py` | Генераторы SQL (опционально) |

**Не загружаются:** база `.fdb`, папка `_pril_v1`, бинарники (см. `.gitignore`).
