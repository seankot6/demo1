# Модуль 3 — Поиск, фильтр, CRUD товаров (пошагово + код)

**Время:** 1 час 30 минут.  
**Основа:** проект из [module-02-wpf-app.md](module-02-wpf-app.md) + БД из [module-01-database.md](module-01-database.md).

## Что сдать по модулю 3

- [ ] Навигация между окнами/страницами + кнопка **«Назад»**
- [ ] Заголовок у каждого окна
- [ ] Обработка ошибок (`MessageBox`: ошибка / предупреждение / информация)
- [ ] **Поиск, сортировка, фильтр скидки** — менеджер и администратор (в реальном времени)
- [ ] **Добавление / редактирование / удаление** товара — только администратор
- [ ] Форма редактирования: одно окно, фото 300×200, путь в БД
- [ ] После изменений список товаров обновляется
- [ ] **docx** со скриншотами (рекомендуется, как в модуле 2)

**Не нужно в модуле 3:** полноценные заказы (CRUD заказов — следующие модули).

---

## Отличие ролей в модуле 3

| Функция | Гость / клиент | Менеджер | Администратор |
|---------|----------------|----------|---------------|
| Список товаров | да | да | да |
| Поиск / сортировка / фильтр | нет | да | да |
| Добавить товар | нет | нет | да |
| Редактировать (клик по строке) | нет | нет | да |
| Удалить | нет | нет | да |

---

## План на 90 минут

| Мин | Задача |
|-----|--------|
| 0–10 | NuGet `System.Drawing.Common`, файлы-хелперы |
| 10–25 | Панель поиска/сортировки/фильтра на `ProductsView` |
| 25–50 | Окно `ProductEditWindow` (добавление + редактирование + фото) |
| 50–65 | Удаление, проверка «товар в заказе», обновление списка |
| 65–75 | Кнопка «Назад», заглушка «Заказы», `try/catch` |
| 75–90 | Проверка ролей, скриншоты в Word |

---

## Шаг 1. NuGet

**Управление пакетами NuGet** → установи:

- `System.Drawing.Common` (изменение размера фото до 300×200)

---

## Шаг 2. Новые файлы в проекте

```
BookStoreApp/
  Helpers/
    AppMessages.cs
    ImageHelper.cs
  Models/
    LookupItem.cs
  Data/
    DatabaseHelper.cs      ← дополнить методами
  Views/
    ProductsView.xaml      ← заменить
    ProductsView.xaml.cs   ← заменить
    OrdersView.xaml        ← новый (заглушка + Назад)
    OrdersView.xaml.cs
  Windows/
    ProductEditWindow.xaml
    ProductEditWindow.xaml.cs
```

**MainWindow.xaml.cs** — передавать сессию в `ProductsView` и `OrdersView`.

---

## Шаг 3. Models/LookupItem.cs

```csharp
namespace BookStoreApp.Models;

public class LookupItem
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public override string ToString() => Name;
}
```

---

## Шаг 4. Helpers/AppMessages.cs

```csharp
using System.Windows;

namespace BookStoreApp.Helpers;

public static class AppMessages
{
    public static void ShowError(string text, string title = "Ошибка") =>
        MessageBox.Show(text, title, MessageBoxButton.OK, MessageBoxImage.Error);

    public static void ShowWarning(string text, string title = "Предупреждение") =>
        MessageBox.Show(text, title, MessageBoxButton.OK, MessageBoxImage.Warning);

    public static void ShowInfo(string text, string title = "Информация") =>
        MessageBox.Show(text, title, MessageBoxButton.OK, MessageBoxImage.Information);

    public static bool Confirm(string text, string title = "Подтверждение") =>
        MessageBox.Show(text, title, MessageBoxButton.YesNo, MessageBoxImage.Question) == MessageBoxResult.Yes;
}
```

---

## Шаг 5. Helpers/ImageHelper.cs

```csharp
using System.Drawing;
using System.Drawing.Drawing2D;
using System.IO;

namespace BookStoreApp.Helpers;

public static class ImageHelper
{
    public static void SaveResizedJpeg(string sourcePath, string destPath, int width = 300, int height = 200)
    {
        using var src = Image.FromFile(sourcePath);
        using var bmp = new Bitmap(width, height);
        using var g = Graphics.FromImage(bmp);
        g.CompositingQuality = CompositingQuality.HighQuality;
        g.InterpolationMode = InterpolationMode.HighQualityBicubic;
        g.DrawImage(src, 0, 0, width, height);
        Directory.CreateDirectory(Path.GetDirectoryName(destPath)!);
        bmp.Save(destPath, System.Drawing.Imaging.ImageFormat.Jpeg);
    }

    public static void TryDeleteAppImage(string? relativePath)
    {
        if (string.IsNullOrWhiteSpace(relativePath)) return;
        if (relativePath.Contains("picture.png", StringComparison.OrdinalIgnoreCase)) return;

        string full = Path.Combine(App.AppFolder, relativePath.Replace('/', Path.DirectorySeparatorChar));
        if (File.Exists(full))
        {
            try { File.Delete(full); } catch { /* игнор при блокировке файла */ }
        }
    }
}
```

---

## Шаг 6. Дополнить Data/DatabaseHelper.cs

**Добавь** в существующий класс (подключение `ConnectionString` уже есть из модуля 2):

```csharp
using BookStoreApp.Helpers;
using BookStoreApp.Models;

// ... внутри public static class DatabaseHelper

public static List<LookupItem> GetCategories()
{
    return GetLookup("SELECT CATEGORY_ID, CATEGORY_NAME FROM CATEGORY ORDER BY CATEGORY_NAME");
}

public static List<LookupItem> GetManufacturers() =>
    GetLookup("SELECT MANUFACTURER_ID, MANUFACTURER_NAME FROM MANUFACTURER ORDER BY MANUFACTURER_NAME");

public static List<LookupItem> GetSuppliers() =>
    GetLookup("SELECT SUPPLIER_ID, SUPPLIER_NAME FROM SUPPLIER ORDER BY SUPPLIER_NAME");

private static List<LookupItem> GetLookup(string sql)
{
    var list = new List<LookupItem>();
    using var conn = new FbConnection(ConnectionString);
    conn.Open();
    using var cmd = new FbCommand(sql, conn);
    using var r = cmd.ExecuteReader();
    while (r.Read())
        list.Add(new LookupItem { Id = r.GetInt32(0), Name = r.GetString(1) });
    return list;
}

public static int GetNextProductId()
{
    using var conn = new FbConnection(ConnectionString);
    conn.Open();
    using var cmd = new FbCommand("SELECT COALESCE(MAX(PRODUCT_ID), 0) + 1 FROM PRODUCT", conn);
    return Convert.ToInt32(cmd.ExecuteScalar());
}

public static bool IsProductInOrders(int productId)
{
    using var conn = new FbConnection(ConnectionString);
    conn.Open();
    using var cmd = new FbCommand("SELECT COUNT(*) FROM ORDER_ITEM WHERE PRODUCT_ID = @id", conn);
    cmd.Parameters.AddWithValue("@id", productId);
    return Convert.ToInt32(cmd.ExecuteScalar()) > 0;
}

public static void InsertProduct(int id, string article, string name, string unit,
    decimal price, int categoryId, int manufacturerId, int supplierId,
    decimal discount, int quantity, string? description, string? photoPath)
{
    const string sql = @"
INSERT INTO PRODUCT (PRODUCT_ID, ARTICLE, PRODUCT_NAME, UNIT_MEASURE, PRICE,
  CATEGORY_ID, MANUFACTURER_ID, SUPPLIER_ID, DISCOUNT, QUANTITY_STOCK, DESCRIPTION, PHOTO_PATH)
VALUES (@id, @art, @name, @unit, @price, @cat, @man, @sup, @disc, @qty, @desc, @photo)";

    using var conn = new FbConnection(ConnectionString);
    conn.Open();
    using var cmd = new FbCommand(sql, conn);
    cmd.Parameters.AddWithValue("@id", id);
    cmd.Parameters.AddWithValue("@art", article);
    cmd.Parameters.AddWithValue("@name", name);
    cmd.Parameters.AddWithValue("@unit", unit);
    cmd.Parameters.AddWithValue("@price", price);
    cmd.Parameters.AddWithValue("@cat", categoryId);
    cmd.Parameters.AddWithValue("@man", manufacturerId);
    cmd.Parameters.AddWithValue("@sup", supplierId);
    cmd.Parameters.AddWithValue("@disc", discount);
    cmd.Parameters.AddWithValue("@qty", quantity);
    cmd.Parameters.AddWithValue("@desc", (object?)description ?? DBNull.Value);
    cmd.Parameters.AddWithValue("@photo", (object?)photoPath ?? DBNull.Value);
    cmd.ExecuteNonQuery();
}

public static void UpdateProduct(int id, string article, string name, string unit,
    decimal price, int categoryId, int manufacturerId, int supplierId,
    decimal discount, int quantity, string? description, string? photoPath)
{
    const string sql = @"
UPDATE PRODUCT SET ARTICLE=@art, PRODUCT_NAME=@name, UNIT_MEASURE=@unit, PRICE=@price,
  CATEGORY_ID=@cat, MANUFACTURER_ID=@man, SUPPLIER_ID=@sup, DISCOUNT=@disc,
  QUANTITY_STOCK=@qty, DESCRIPTION=@desc, PHOTO_PATH=@photo
WHERE PRODUCT_ID=@id";

    using var conn = new FbConnection(ConnectionString);
    conn.Open();
    using var cmd = new FbCommand(sql, conn);
    cmd.Parameters.AddWithValue("@id", id);
    cmd.Parameters.AddWithValue("@art", article);
    cmd.Parameters.AddWithValue("@name", name);
    cmd.Parameters.AddWithValue("@unit", unit);
    cmd.Parameters.AddWithValue("@price", price);
    cmd.Parameters.AddWithValue("@cat", categoryId);
    cmd.Parameters.AddWithValue("@man", manufacturerId);
    cmd.Parameters.AddWithValue("@sup", supplierId);
    cmd.Parameters.AddWithValue("@disc", discount);
    cmd.Parameters.AddWithValue("@qty", quantity);
    cmd.Parameters.AddWithValue("@desc", (object?)description ?? DBNull.Value);
    cmd.Parameters.AddWithValue("@photo", (object?)photoPath ?? DBNull.Value);
    cmd.ExecuteNonQuery();
}

public static void DeleteProduct(int productId)
{
    using var conn = new FbConnection(ConnectionString);
    conn.Open();
    using var cmd = new FbCommand("DELETE FROM PRODUCT WHERE PRODUCT_ID=@id", conn);
    cmd.Parameters.AddWithValue("@id", productId);
    cmd.ExecuteNonQuery();
}

public static string? GetProductPhotoPath(int productId)
{
    using var conn = new FbConnection(ConnectionString);
    conn.Open();
    using var cmd = new FbCommand("SELECT PHOTO_PATH FROM PRODUCT WHERE PRODUCT_ID=@id", conn);
    cmd.Parameters.AddWithValue("@id", productId);
    var v = cmd.ExecuteScalar();
    return v == DBNull.Value ? null : Convert.ToString(v);
}

public static string SaveProductImageFromFile(string sourceFile, int productId)
{
    string fileName = $"{productId}.jpg";
    string destFull = Path.Combine(App.ImportFolder, fileName);
    ImageHelper.SaveResizedJpeg(sourceFile, destFull, 300, 200);
    return $"import\\{fileName}";
}
```

---

## Шаг 7. Windows/ProductEditWindow.xaml

**Добавить** → **Окно WPF** → `ProductEditWindow.xaml`.

```xml
<Window x:Class="BookStoreApp.Windows.ProductEditWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Товар" Height="620" Width="520"
        WindowStartupLocation="CenterOwner" ResizeMode="NoResize">
    <Grid Margin="15">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <TextBlock x:Name="TxtId" Grid.Row="0" Margin="0,0,0,10"/>

        <ScrollViewer Grid.Row="1">
            <StackPanel>
                <Image x:Name="ImgPreview" Height="120" Stretch="Uniform" Margin="0,0,0,5"/>
                <Button x:Name="BtnPickPhoto" Content="Выбрать фото" Click="BtnPickPhoto_Click"/>

                <TextBlock Text="Артикул:" Margin="0,10,0,0"/>
                <TextBox x:Name="TxtArticle"/>

                <TextBlock Text="Наименование:" Margin="0,8,0,0"/>
                <TextBox x:Name="TxtName"/>

                <TextBlock Text="Категория:" Margin="0,8,0,0"/>
                <ComboBox x:Name="CmbCategory" DisplayMemberPath="Name"/>

                <TextBlock Text="Описание:" Margin="0,8,0,0"/>
                <TextBox x:Name="TxtDescription" Height="60" TextWrapping="Wrap" AcceptsReturn="True"/>

                <TextBlock Text="Производитель:" Margin="0,8,0,0"/>
                <ComboBox x:Name="CmbManufacturer" DisplayMemberPath="Name"/>

                <TextBlock Text="Поставщик:" Margin="0,8,0,0"/>
                <ComboBox x:Name="CmbSupplier" DisplayMemberPath="Name"/>

                <TextBlock Text="Цена:" Margin="0,8,0,0"/>
                <TextBox x:Name="TxtPrice"/>

                <TextBlock Text="Ед. изм.:" Margin="0,8,0,0"/>
                <TextBox x:Name="TxtUnit"/>

                <TextBlock Text="На складе:" Margin="0,8,0,0"/>
                <TextBox x:Name="TxtQuantity"/>

                <TextBlock Text="Скидка %:" Margin="0,8,0,0"/>
                <TextBox x:Name="TxtDiscount"/>
            </StackPanel>
        </ScrollViewer>

        <StackPanel Grid.Row="2" Orientation="Horizontal" HorizontalAlignment="Right" Margin="0,15,0,0">
            <Button Content="Назад" Width="100" Click="BtnBack_Click"/>
            <Button Content="Сохранить" Width="100" Click="BtnSave_Click"/>
        </StackPanel>
    </Grid>
</Window>
```

---

## Шаг 8. Windows/ProductEditWindow.xaml.cs

```csharp
using System.Globalization;
using System.Windows;
using System.Windows.Media.Imaging;
using BookStoreApp.Data;
using BookStoreApp.Helpers;
using BookStoreApp.Models;
using BookStoreApp.Views;
using Microsoft.Win32;

namespace BookStoreApp.Windows;

public partial class ProductEditWindow : Window
{
    private static bool _isOpen;

    private readonly int? _productId;
    private string? _photoPath;
    private string? _pendingPhotoSource;

    public ProductEditWindow(ProductRowView? product)
    {
        if (_isOpen)
        {
            AppMessages.ShowWarning(
                "Окно редактирования уже открыто. Закройте его, чтобы изменить другой товар.",
                "Редактирование");
            throw new InvalidOperationException("Edit window already open");
        }

        _isOpen = true;
        InitializeComponent();
        _productId = product?.ProductId;

        Title = _productId == null ? "Добавление товара" : "Редактирование товара";
        TxtId.Visibility = _productId == null ? Visibility.Collapsed : Visibility.Visible;
        if (_productId != null)
            TxtId.Text = $"ID: {_productId}";

        LoadCombos();
        if (product != null)
            FillForm(product);
        else
            ImgPreview.Source = new BitmapImage(new Uri(App.PicturePlaceholder));
    }

    protected override void OnClosed(EventArgs e)
    {
        _isOpen = false;
        base.OnClosed(e);
    }

    private void LoadCombos()
    {
        try
        {
            CmbCategory.ItemsSource = DatabaseHelper.GetCategories();
            CmbManufacturer.ItemsSource = DatabaseHelper.GetManufacturers();
            CmbSupplier.ItemsSource = DatabaseHelper.GetSuppliers();
        }
        catch (Exception ex)
        {
            AppMessages.ShowError("Не удалось загрузить справочники:\n" + ex.Message);
        }
    }

    private void FillForm(ProductRowView p)
    {
        TxtArticle.Text = p.Article;
        TxtName.Text = p.ProductName;
        TxtDescription.Text = p.Description;
        TxtPrice.Text = p.Price.ToString(CultureInfo.InvariantCulture);
        TxtUnit.Text = p.UnitMeasure;
        TxtQuantity.Text = p.QuantityStock.ToString();
        TxtDiscount.Text = p.Discount.ToString(CultureInfo.InvariantCulture);
        _photoPath = p.PhotoPath;

        SelectCombo(CmbCategory, p.CategoryName);
        SelectCombo(CmbManufacturer, p.ManufacturerName);
        SelectCombo(CmbSupplier, p.SupplierName);

        ImgPreview.Source = new BitmapImage(new Uri(p.PhotoFullPath));
    }

    private static void SelectCombo(System.Windows.Controls.ComboBox cmb, string name)
    {
        foreach (LookupItem item in cmb.Items)
            if (item.Name == name) { cmb.SelectedItem = item; break; }
    }

    private void BtnPickPhoto_Click(object sender, RoutedEventArgs e)
    {
        var dlg = new OpenFileDialog
        {
            Filter = "Изображения|*.jpg;*.jpeg;*.png;*.bmp"
        };
        if (dlg.ShowDialog() != true) return;

        _pendingPhotoSource = dlg.FileName;
        ImgPreview.Source = new BitmapImage(new Uri(dlg.FileName));
    }

    private void BtnBack_Click(object sender, RoutedEventArgs e)
    {
        DialogResult = false;
        Close();
    }

    private void BtnSave_Click(object sender, RoutedEventArgs e)
    {
        if (!ValidateForm(out var article, out var name, out var unit, out var price,
                out var qty, out var discount, out var categoryId, out var manId, out var supId))
            return;

        try
        {
            int id = _productId ?? DatabaseHelper.GetNextProductId();
            string? description = string.IsNullOrWhiteSpace(TxtDescription.Text) ? null : TxtDescription.Text.Trim();
            string? photo = _photoPath;

            if (_pendingPhotoSource != null)
            {
                if (_productId != null)
                    ImageHelper.TryDeleteAppImage(DatabaseHelper.GetProductPhotoPath(_productId.Value));
                photo = DatabaseHelper.SaveProductImageFromFile(_pendingPhotoSource, id);
            }

            if (_productId == null)
            {
                DatabaseHelper.InsertProduct(id, article, name, unit, price, categoryId, manId, supId,
                    discount, qty, description, photo);
                AppMessages.ShowInfo("Товар добавлен.", "Успех");
            }
            else
            {
                DatabaseHelper.UpdateProduct(id, article, name, unit, price, categoryId, manId, supId,
                    discount, qty, description, photo);
                AppMessages.ShowInfo("Товар обновлён.", "Успех");
            }

            DialogResult = true;
            Close();
        }
        catch (Exception ex)
        {
            AppMessages.ShowError(
                "Не удалось сохранить товар.\n" + ex.Message +
                "\n\nПроверьте подключение к БД и уникальность артикула.");
        }
    }

    private bool ValidateForm(out string article, out string name, out string unit,
        out decimal price, out int qty, out decimal discount,
        out int categoryId, out int manId, out int supId)
    {
        article = TxtArticle.Text.Trim();
        name = TxtName.Text.Trim();
        unit = TxtUnit.Text.Trim();

        if (string.IsNullOrEmpty(article) || string.IsNullOrEmpty(name) || string.IsNullOrEmpty(unit))
        {
            AppMessages.ShowWarning("Заполните артикул, наименование и единицу измерения.");
            price = 0; qty = 0; discount = 0; categoryId = manId = supId = 0;
            return false;
        }

        if (!decimal.TryParse(TxtPrice.Text.Replace(',', '.'), NumberStyles.Any,
                CultureInfo.InvariantCulture, out price) || price < 0)
        {
            AppMessages.ShowWarning("Цена должна быть числом ≥ 0 (можно с копейками).");
            qty = 0; discount = 0; categoryId = manId = supId = 0;
            return false;
        }

        if (!int.TryParse(TxtQuantity.Text, out qty) || qty < 0)
        {
            AppMessages.ShowWarning("Количество на складе — целое число ≥ 0.");
            discount = 0; categoryId = manId = supId = 0;
            return false;
        }

        if (!decimal.TryParse(TxtDiscount.Text.Replace(',', '.'), NumberStyles.Any,
                CultureInfo.InvariantCulture, out discount) || discount < 0)
        {
            AppMessages.ShowWarning("Скидка — число ≥ 0.");
            categoryId = manId = supId = 0;
            return false;
        }

        if (CmbCategory.SelectedItem is not LookupItem cat ||
            CmbManufacturer.SelectedItem is not LookupItem man ||
            CmbSupplier.SelectedItem is not LookupItem sup)
        {
            AppMessages.ShowWarning("Выберите категорию, производителя и поставщика.");
            categoryId = manId = supId = 0;
            return false;
        }

        categoryId = cat.Id;
        manId = man.Id;
        supId = sup.Id;
        return true;
    }
}
```

---

## Шаг 9. Views/OrdersView.xaml (заглушка + «Назад»)

```xml
<UserControl x:Class="BookStoreApp.Views.OrdersView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <Grid Background="{StaticResource MainBg}">
        <StackPanel VerticalAlignment="Center" HorizontalAlignment="Center">
            <TextBlock Text="Раздел «Заказы»" FontSize="20" FontWeight="Bold" HorizontalAlignment="Center"/>
            <TextBlock Text="Полный функционал — в следующих модулях." Margin="0,10,0,20"
                       HorizontalAlignment="Center"/>
            <Button Content="Назад" Width="120" HorizontalAlignment="Center" Click="BtnBack_Click"/>
        </StackPanel>
    </Grid>
</UserControl>
```

```csharp
using System.Windows;
using System.Windows.Controls;
using BookStoreApp.Models;

namespace BookStoreApp.Views;

public partial class OrdersView : UserControl
{
    public event EventHandler? BackRequested;

    public OrdersView() => InitializeComponent();

    private void BtnBack_Click(object sender, RoutedEventArgs e) =>
        BackRequested?.Invoke(this, EventArgs.Empty);
}
```

---

## Шаг 10. Views/ProductsView.xaml (заменить целиком)

```xml
<UserControl x:Class="BookStoreApp.Views.ProductsView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <UserControl.Resources>
        <BooleanToVisibilityConverter x:Key="BoolToVis"/>
    </UserControl.Resources>
    <Grid Background="{StaticResource MainBg}">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
        </Grid.RowDefinitions>

        <StackPanel x:Name="PanelAdmin" Grid.Row="0" Orientation="Horizontal" Margin="0,0,0,5">
            <Button x:Name="BtnAdd" Content="Добавить товар" Click="BtnAdd_Click"/>
            <Button x:Name="BtnDelete" Content="Удалить товар" Click="BtnDelete_Click"/>
        </StackPanel>

        <Border x:Name="PanelSearch" Grid.Row="1" Background="{StaticResource ExtraBg}"
                Padding="8" Margin="0,0,0,5">
            <WrapPanel>
                <TextBlock Text="Поиск:" VerticalAlignment="Center" Margin="0,0,5,0"/>
                <TextBox x:Name="TxtSearch" Width="200" TextChanged="FilterChanged"/>

                <TextBlock Text="Сортировка:" VerticalAlignment="Center" Margin="15,0,5,0"/>
                <ComboBox x:Name="CmbSortField" Width="140" SelectionChanged="FilterChanged">
                    <ComboBoxItem Content="По цене" IsSelected="True"/>
                    <ComboBoxItem Content="По количеству"/>
                </ComboBox>
                <ComboBox x:Name="CmbSortDir" Width="130" SelectionChanged="FilterChanged">
                    <ComboBoxItem Content="По возрастанию" IsSelected="True"/>
                    <ComboBoxItem Content="По убыванию"/>
                </ComboBox>

                <TextBlock Text="Скидка:" VerticalAlignment="Center" Margin="15,0,5,0"/>
                <ComboBox x:Name="CmbDiscount" Width="160" SelectionChanged="FilterChanged">
                    <ComboBoxItem Content="Все диапазоны" IsSelected="True"/>
                    <ComboBoxItem Content="0–12,99%"/>
                    <ComboBoxItem Content="13–16,99%"/>
                    <ComboBoxItem Content="17% и более"/>
                </ComboBox>
            </WrapPanel>
        </Border>

        <DataGrid x:Name="ProductsGrid" Grid.Row="2"
                  AutoGenerateColumns="False" IsReadOnly="True"
                  CanUserAddRows="False" LoadingRow="ProductsGrid_LoadingRow"
                  MouseDoubleClick="ProductsGrid_MouseDoubleClick"
                  FontFamily="{StaticResource AppFont}">
            <!-- те же колонки, что в модуле 2 — см. module-02-wpf-app.md -->
        </DataGrid>
    </Grid>
</UserControl>
```

Скопируй блок `<DataGrid.Columns>...</DataGrid.Columns>` из [module-02-wpf-app.md](module-02-wpf-app.md) без изменений.

---

## Шаг 11. Views/ProductsView.xaml.cs (заменить целиком)

```csharp
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using BookStoreApp.Data;
using BookStoreApp.Helpers;
using BookStoreApp.Models;
using BookStoreApp.Windows;

namespace BookStoreApp.Views;

public partial class ProductsView : UserControl
{
    private readonly UserSession _session;
    private List<ProductRowView> _all = new();

    public ProductsView(UserSession session)
    {
        _session = session;
        InitializeComponent();

        bool canFilter = _session.IsManager || _session.IsAdmin;
        PanelSearch.Visibility = canFilter ? Visibility.Visible : Visibility.Collapsed;
        PanelAdmin.Visibility = _session.IsAdmin ? Visibility.Visible : Visibility.Collapsed;

        LoadData();
    }

    public void Reload() => LoadData();

    private void LoadData()
    {
        try
        {
            _all = DatabaseHelper.GetProducts().Select(ProductRowView.From).ToList();
            ApplyFilters();
        }
        catch (Exception ex)
        {
            AppMessages.ShowError("Не удалось загрузить товары:\n" + ex.Message);
        }
    }

    private void FilterChanged(object sender, RoutedEventArgs e) => ApplyFilters();

    private void ApplyFilters()
    {
        IEnumerable<ProductRowView> q = _all;

        string search = TxtSearch?.Text?.Trim().ToLower() ?? "";
        if (!string.IsNullOrEmpty(search))
        {
            q = q.Where(p =>
                p.Article.ToLower().Contains(search) ||
                p.ProductName.ToLower().Contains(search) ||
                p.CategoryName.ToLower().Contains(search) ||
                (p.Description ?? "").ToLower().Contains(search) ||
                p.ManufacturerName.ToLower().Contains(search) ||
                p.SupplierName.ToLower().Contains(search) ||
                p.UnitMeasure.ToLower().Contains(search));
        }

        switch (CmbDiscount?.SelectedIndex ?? 0)
        {
            case 1: q = q.Where(p => p.Discount >= 0 && p.Discount <= 12.99m); break;
            case 2: q = q.Where(p => p.Discount >= 13 && p.Discount <= 16.99m); break;
            case 3: q = q.Where(p => p.Discount >= 17); break;
        }

        bool byPrice = (CmbSortField?.SelectedIndex ?? 0) == 0;
        bool desc = (CmbSortDir?.SelectedIndex ?? 0) == 1;

        q = byPrice
            ? (desc ? q.OrderByDescending(p => p.Price) : q.OrderBy(p => p.Price))
            : (desc ? q.OrderByDescending(p => p.QuantityStock) : q.OrderBy(p => p.QuantityStock));

        ProductsGrid.ItemsSource = q.ToList();
    }

    private void ProductsGrid_LoadingRow(object sender, DataGridRowEventArgs e)
    {
        if (e.Row.Item is not ProductRowView item) return;
        if (item.IsOutOfStock) e.Row.Background = Brushes.LightGray;
        else if (item.IsHighDiscount) e.Row.Background = (Brush)FindResource("DiscountBg");
        else e.Row.Background = Brushes.White;
    }

    private void ProductsGrid_MouseDoubleClick(object sender, System.Windows.Input.MouseButtonEventArgs e)
    {
        if (!_session.IsAdmin) return;
        if (ProductsGrid.SelectedItem is not ProductRowView row) return;
        OpenEdit(row);
    }

    private void BtnAdd_Click(object sender, RoutedEventArgs e) => OpenEdit(null);

    private void OpenEdit(ProductRowView? row)
    {
        try
        {
            var win = new ProductEditWindow(row) { Owner = Window.GetWindow(this) };
            if (win.ShowDialog() == true)
                LoadData();
        }
        catch (InvalidOperationException) { /* второе окно — предупреждение уже показано */ }
    }

    private void BtnDelete_Click(object sender, RoutedEventArgs e)
    {
        if (ProductsGrid.SelectedItem is not ProductRowView row)
        {
            AppMessages.ShowWarning("Выберите товар в таблице для удаления.");
            return;
        }

        try
        {
            if (DatabaseHelper.IsProductInOrders(row.ProductId))
            {
                AppMessages.ShowWarning(
                    $"Товар «{row.ProductName}» нельзя удалить: он есть в заказе.",
                    "Удаление запрещено");
                return;
            }

            if (!AppMessages.Confirm($"Удалить товар «{row.ProductName}»?", "Удаление"))
                return;

            ImageHelper.TryDeleteAppImage(row.PhotoPath);
            DatabaseHelper.DeleteProduct(row.ProductId);
            AppMessages.ShowInfo("Товар удалён.");
            LoadData();
        }
        catch (Exception ex)
        {
            AppMessages.ShowError("Ошибка удаления:\n" + ex.Message);
        }
    }
}
```

---

## Шаг 12. MainWindow.xaml.cs (навигация)

```csharp
using System.Windows;
using BookStoreApp.Models;
using BookStoreApp.Views;

namespace BookStoreApp;

public partial class MainWindow : Window
{
    private readonly UserSession _session;

    public MainWindow(UserSession session)
    {
        InitializeComponent();
        _session = session;

        Title = "ЧитайГород — " + _session.RoleName;
        TxtTitle.Text = "Список товаров";
        TxtUserInfo.Text = _session.IsGuest ? "Гость" : $"ФИО: {_session.FullName}";
        BtnOrders.Visibility = _session.CanViewOrders ? Visibility.Visible : Visibility.Collapsed;

        ShowProducts();
    }

    private void ShowProducts()
    {
        TxtTitle.Text = "Список товаров";
        MainContent.Content = new ProductsView(_session);
    }

    private void BtnOrders_Click(object sender, RoutedEventArgs e)
    {
        TxtTitle.Text = "Заказы";
        var orders = new OrdersView();
        orders.BackRequested += (_, _) => ShowProducts();
        MainContent.Content = orders;
    }

    private void BtnLogout_Click(object sender, RoutedEventArgs e)
    {
        new LoginWindow().Show();
        Close();
    }
}
```

---

## Шаг 13. Проверка перед сдачей

### Менеджер (`ptec8ym@yahoo.com` / `LdNyos`)

- [ ] Видна панель поиска / сортировки / фильтра  
- [ ] Поиск без кнопки «Найти» — сразу при вводе  
- [ ] Фильтр «17% и более» + поиск работают вместе  
- [ ] Сортировка по цене сохраняется при фильтре  
- [ ] Нет кнопок «Добавить» / «Удалить», двойной клик не открывает форму  

### Администратор (`94d5ous@gmail.com` / `uzWC67`)

- [ ] Добавление товара, ID = MAX+1  
- [ ] Редактирование по двойному клику, ID только чтение  
- [ ] Второе окно редактирования не открывается  
- [ ] Фото сохраняется в `import\`, размер 300×200  
- [ ] Удаление товара из заказа (например ID 1) — **запрещено**  
- [ ] Удаление товара без заказов — работает  
- [ ] Список обновляется после сохранения  

### Ошибки

- [ ] Пустые поля / отрицательная цена — предупреждение  
- [ ] Нет падения приложения при ошибке БД  

---

## Чек-лист модуля 3

- [ ] «Назад» с формы товара и с экрана «Заказы»  
- [ ] Заголовки окон корректные  
- [ ] MessageBox с иконками Error / Warning / Information  
- [ ] Поиск + фильтр + сортировка в реальном времени  
- [ ] CRUD товаров только у администратора  
- [ ] docx со скриншотами  

---

## Связь с другими модулями

| Модуль | Содержание |
|--------|------------|
| 1 | [module-01-database.md](module-01-database.md), [sql/module-01-full.sql](../sql/module-01-full.sql) |
| 2 | [module-02-wpf-app.md](module-02-wpf-app.md) — база приложения |
| 3 | этот файл |
| 4+ | заказы (просмотр/редактирование) — по заданию ДЭ |
