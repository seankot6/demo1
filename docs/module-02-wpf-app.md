# Модуль 2 — WPF-приложение (пошагово + весь код)

**Время:** 40 минут.  
**Стек:** C# + WPF + Firebird (`FirebirdSql.Data.FirebirdClient`).

## Что сдать по модулю 2

- [ ] Блок-схема алгоритма (ГОСТ 19.701-90) → **PDF**
- [ ] Приложение с подключением к `database.fdb`
- [ ] Окно входа + гость + интерфейсы ролей
- [ ] Список товаров из БД (оформление по заданию)
- [ ] **docx** со скриншотами

**Не нужно в модуле 2:** поиск, фильтр, сортировка, CRUD товаров (модуль 3).

---

## Стиль (Прил_3)

| Элемент | Значение |
|---------|----------|
| Шрифт | Comic Sans MS |
| Основной фон | `#FFFFFF` |
| Доп. фон | `#ABCFCE` |
| Кнопки (акцент) | `#546F94` |
| Скидка > 25% (фон строки) | `#23E1EF` |

---

## Шаг 0. Создание проекта

1. Visual Studio → **Приложение WPF** → имя `BookStoreApp`
2. NuGet: **`FirebirdSql.Data.FirebirdClient`**
3. Скопируй папку **`import`** из архива задания в проект
4. Для файлов в `import\`: **Свойства** → **Копировать в выходной каталог** = **Копировать, если новее**
5. `logo.png` — логотип из ресурсов (или `import\icon.png`)

**App.xaml** — в свойствах проекта **Объект запуска** можно оставить через `StartupUri="LoginWindow.xaml"`.

---

## Структура файлов

```
BookStoreApp/
  App.xaml
  App.xaml.cs
  LoginWindow.xaml
  LoginWindow.xaml.cs
  MainWindow.xaml
  MainWindow.xaml.cs
  Models/UserSession.cs
  Models/ProductItem.cs
  Data/DatabaseHelper.cs
  Views/ProductsView.xaml
  Views/ProductsView.xaml.cs
  Views/ProductRowView.cs
  import/
  logo.png
```

---

## Код: App.xaml

```xml
<Application x:Class="BookStoreApp.App"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             StartupUri="LoginWindow.xaml">
    <Application.Resources>
        <FontFamily x:Key="AppFont">Comic Sans MS</FontFamily>
        <SolidColorBrush x:Key="MainBg" Color="#FFFFFF"/>
        <SolidColorBrush x:Key="ExtraBg" Color="#ABCFCE"/>
        <SolidColorBrush x:Key="AccentBg" Color="#546F94"/>
        <SolidColorBrush x:Key="DiscountBg" Color="#23E1EF"/>
        <Style TargetType="Window">
            <Setter Property="FontFamily" Value="{StaticResource AppFont}"/>
            <Setter Property="Background" Value="{StaticResource MainBg}"/>
        </Style>
        <Style TargetType="Button">
            <Setter Property="FontFamily" Value="{StaticResource AppFont}"/>
            <Setter Property="Background" Value="{StaticResource AccentBg}"/>
            <Setter Property="Foreground" Value="White"/>
            <Setter Property="Padding" Value="10,5"/>
            <Setter Property="Margin" Value="5"/>
        </Style>
        <Style TargetType="TextBox">
            <Setter Property="FontFamily" Value="{StaticResource AppFont}"/>
            <Setter Property="Margin" Value="5"/>
            <Setter Property="Padding" Value="4"/>
        </Style>
        <Style TargetType="TextBlock">
            <Setter Property="FontFamily" Value="{StaticResource AppFont}"/>
        </Style>
    </Application.Resources>
</Application>
```

---

## Код: App.xaml.cs

```csharp
using System.IO;
using System.Windows;

namespace BookStoreApp;

public partial class App : Application
{
    public static string AppFolder =>
        Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location)!;

    public static string ImportFolder =>
        Path.Combine(AppFolder, "import");

    public static string PicturePlaceholder =>
        Path.Combine(ImportFolder, "picture.png");
}
```

---

## Код: Models/UserSession.cs

```csharp
namespace BookStoreApp.Models;

public class UserSession
{
    public int? UserId { get; set; }
    public string FullName { get; set; } = "";
    public string RoleName { get; set; } = "";

    public bool IsGuest => RoleName == "Гость";
    public bool IsAdmin => RoleName == "Администратор";
    public bool IsManager => RoleName == "Менеджер";
    public bool IsClient => RoleName == "Авторизированный клиент";
    public bool CanViewOrders => IsAdmin || IsManager;
}
```

---

## Код: Models/ProductItem.cs

```csharp
namespace BookStoreApp.Models;

public class ProductItem
{
    public int ProductId { get; set; }
    public string Article { get; set; } = "";
    public string ProductName { get; set; } = "";
    public string CategoryName { get; set; } = "";
    public string Description { get; set; } = "";
    public string ManufacturerName { get; set; } = "";
    public string SupplierName { get; set; } = "";
    public decimal Price { get; set; }
    public string UnitMeasure { get; set; } = "";
    public int QuantityStock { get; set; }
    public decimal Discount { get; set; }
    public string PhotoPath { get; set; } = "";

    public decimal FinalPrice => Price - Price * Discount / 100m;
    public bool HasDiscount => Discount > 0;
    public bool IsHighDiscount => Discount > 25;
    public bool IsOutOfStock => QuantityStock <= 0;
}
```

---

## Код: Data/DatabaseHelper.cs

Путь к БД: `C:\BookStore\database.fdb` — измени при необходимости.

```csharp
using System.IO;
using BookStoreApp.Models;
using FirebirdSql.Data.FirebirdClient;

namespace BookStoreApp.Data;

public static class DatabaseHelper
{
    private const string DbPath = @"C:\BookStore\database.fdb";

    private static string ConnectionString =>
        new FbConnectionStringBuilder
        {
            Database = DbPath,
            UserID = "SYSDBA",
            Password = "masterkey",
            Charset = "UTF8",
            ServerType = FbServerType.Embedded
        }.ToString();

    public static UserSession? TryLogin(string login, string password)
    {
        const string sql = @"
SELECT u.USER_ID, u.FULL_NAME, r.ROLE_NAME
FROM USERS u
INNER JOIN ROLE r ON r.ROLE_ID = u.ROLE_ID
WHERE u.LOGIN = @login AND u.PASSWORD = @password";

        using var conn = new FbConnection(ConnectionString);
        conn.Open();
        using var cmd = new FbCommand(sql, conn);
        cmd.Parameters.AddWithValue("@login", login.Trim());
        cmd.Parameters.AddWithValue("@password", password);

        using var reader = cmd.ExecuteReader();
        if (!reader.Read())
            return null;

        return new UserSession
        {
            UserId = reader.GetInt32(0),
            FullName = reader.GetString(1),
            RoleName = reader.GetString(2)
        };
    }

    public static List<ProductItem> GetProducts()
    {
        const string sql = @"
SELECT
    p.PRODUCT_ID, p.ARTICLE, p.PRODUCT_NAME,
    c.CATEGORY_NAME, COALESCE(p.DESCRIPTION, ''),
    m.MANUFACTURER_NAME, s.SUPPLIER_NAME,
    p.PRICE, p.UNIT_MEASURE, p.QUANTITY_STOCK,
    COALESCE(p.DISCOUNT, 0), COALESCE(p.PHOTO_PATH, '')
FROM PRODUCT p
INNER JOIN CATEGORY c ON c.CATEGORY_ID = p.CATEGORY_ID
INNER JOIN MANUFACTURER m ON m.MANUFACTURER_ID = p.MANUFACTURER_ID
INNER JOIN SUPPLIER s ON s.SUPPLIER_ID = p.SUPPLIER_ID
ORDER BY p.PRODUCT_NAME";

        var list = new List<ProductItem>();
        using var conn = new FbConnection(ConnectionString);
        conn.Open();
        using var cmd = new FbCommand(sql, conn);
        using var reader = cmd.ExecuteReader();

        while (reader.Read())
        {
            list.Add(new ProductItem
            {
                ProductId = reader.GetInt32(0),
                Article = reader.GetString(1),
                ProductName = reader.GetString(2),
                CategoryName = reader.GetString(3),
                Description = reader.GetString(4),
                ManufacturerName = reader.GetString(5),
                SupplierName = reader.GetString(6),
                Price = reader.GetDecimal(7),
                UnitMeasure = reader.GetString(8),
                QuantityStock = reader.GetInt32(9),
                Discount = reader.GetDecimal(10),
                PhotoPath = reader.GetString(11)
            });
        }
        return list;
    }

    public static string ResolvePhotoPath(string? dbPath)
    {
        if (string.IsNullOrWhiteSpace(dbPath))
            return App.PicturePlaceholder;

        string full = Path.IsPathRooted(dbPath)
            ? dbPath
            : Path.Combine(App.AppFolder, dbPath.Replace('/', Path.DirectorySeparatorChar));

        return File.Exists(full) ? full : App.PicturePlaceholder;
    }
}
```

**Если Embedded не работает**, замени строку подключения:

```csharp
Database = @"localhost:C:\BookStore\database.fdb",
ServerType = FbServerType.Default
```

---

## Код: LoginWindow.xaml

Создай **Окно WPF** `LoginWindow.xaml`.

```xml
<Window x:Class="BookStoreApp.LoginWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Вход в систему — ЧитайГород"
        Height="420" Width="500"
        WindowStartupLocation="CenterScreen"
        Icon="import/icon.ico">
    <Grid Background="{StaticResource MainBg}">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
        </Grid.RowDefinitions>
        <Border Grid.Row="0" Background="{StaticResource ExtraBg}" Padding="15">
            <StackPanel HorizontalAlignment="Center">
                <Image Source="logo.png" Height="80" Stretch="Uniform"/>
                <TextBlock Text="ООО «ЧитайГород»" FontSize="18" FontWeight="Bold"
                           HorizontalAlignment="Center" Margin="0,10,0,0"/>
            </StackPanel>
        </Border>
        <StackPanel Grid.Row="1" Margin="30" VerticalAlignment="Center">
            <TextBlock Text="Логин:"/>
            <TextBox x:Name="TxtLogin"/>
            <TextBlock Text="Пароль:" Margin="0,10,0,0"/>
            <PasswordBox x:Name="TxtPassword" FontFamily="{StaticResource AppFont}" Margin="5" Padding="4"/>
            <TextBlock x:Name="LblError" Foreground="Red" Margin="5" TextWrapping="Wrap"/>
            <StackPanel Orientation="Horizontal" HorizontalAlignment="Center" Margin="0,15,0,0">
                <Button Content="Войти" Width="120" Click="BtnLogin_Click"/>
                <Button Content="Войти как гость" Width="150" Click="BtnGuest_Click"/>
            </StackPanel>
        </StackPanel>
    </Grid>
</Window>
```

---

## Код: LoginWindow.xaml.cs

```csharp
using System.Windows;
using BookStoreApp.Data;
using BookStoreApp.Models;

namespace BookStoreApp;

public partial class LoginWindow : Window
{
    public LoginWindow() => InitializeComponent();

    private void BtnLogin_Click(object sender, RoutedEventArgs e)
    {
        LblError.Text = "";
        string login = TxtLogin.Text.Trim();
        string password = TxtPassword.Password;

        if (string.IsNullOrEmpty(login) || string.IsNullOrEmpty(password))
        {
            LblError.Text = "Введите логин и пароль.";
            return;
        }

        try
        {
            var user = DatabaseHelper.TryLogin(login, password);
            if (user == null)
            {
                LblError.Text = "Неверный логин или пароль.";
                return;
            }
            OpenMain(user);
        }
        catch (Exception ex)
        {
            LblError.Text = "Ошибка БД: " + ex.Message;
        }
    }

    private void BtnGuest_Click(object sender, RoutedEventArgs e) =>
        OpenMain(new UserSession { FullName = "Гость", RoleName = "Гость" });

    private void OpenMain(UserSession session)
    {
        new MainWindow(session).Show();
        Close();
    }
}
```

---

## Код: MainWindow.xaml

```xml
<Window x:Class="BookStoreApp.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="ЧитайГород" Height="700" Width="1100"
        WindowStartupLocation="CenterScreen"
        Icon="import/icon.ico">
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
        </Grid.RowDefinitions>
        <Border Grid.Row="0" Background="{StaticResource ExtraBg}" Padding="10">
            <DockPanel LastChildFill="True">
                <Button DockPanel.Dock="Right" Content="Выйти" Click="BtnLogout_Click"/>
                <Button x:Name="BtnOrders" DockPanel.Dock="Right" Content="Заказы"
                        Click="BtnOrders_Click" Visibility="Collapsed"/>
                <StackPanel Orientation="Horizontal">
                    <Image Source="logo.png" Height="40"/>
                    <TextBlock x:Name="TxtTitle" VerticalAlignment="Center"
                               FontSize="16" FontWeight="Bold" Margin="10,0,0,0"/>
                </StackPanel>
                <TextBlock x:Name="TxtUserInfo" HorizontalAlignment="Right"
                           VerticalAlignment="Center" Margin="0,0,15,0"/>
            </DockPanel>
        </Border>
        <ContentControl x:Name="MainContent" Grid.Row="1" Margin="10"/>
    </Grid>
</Window>
```

---

## Код: MainWindow.xaml.cs

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
        MainContent.Content = new ProductsView();
    }

    private void BtnOrders_Click(object sender, RoutedEventArgs e) =>
        MessageBox.Show("Раздел «Заказы» — заглушка (в ДЭ три модуля; заказы по желанию в мод. 3).", "Заказы",
            MessageBoxButton.OK, MessageBoxImage.Information);

    private void BtnLogout_Click(object sender, RoutedEventArgs e)
    {
        new LoginWindow().Show();
        Close();
    }
}
```

---

## Код: Views/ProductRowView.cs

```csharp
using BookStoreApp.Data;
using BookStoreApp.Models;

namespace BookStoreApp.Views;

public class ProductRowView : ProductItem
{
    public string PhotoFullPath { get; set; } = "";

    public static ProductRowView From(ProductItem p) => new()
    {
        ProductId = p.ProductId,
        Article = p.Article,
        ProductName = p.ProductName,
        CategoryName = p.CategoryName,
        Description = p.Description,
        ManufacturerName = p.ManufacturerName,
        SupplierName = p.SupplierName,
        Price = p.Price,
        UnitMeasure = p.UnitMeasure,
        QuantityStock = p.QuantityStock,
        Discount = p.Discount,
        PhotoPath = p.PhotoPath,
        PhotoFullPath = DatabaseHelper.ResolvePhotoPath(p.PhotoPath)
    };
}
```

---

## Код: Views/ProductsView.xaml

**Добавить** → **Пользовательский элемент (WPF)** → `ProductsView.xaml`.

```xml
<UserControl x:Class="BookStoreApp.Views.ProductsView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <UserControl.Resources>
        <BooleanToVisibilityConverter x:Key="BoolToVis"/>
    </UserControl.Resources>
    <Grid Background="{StaticResource MainBg}">
        <DataGrid x:Name="ProductsGrid" AutoGenerateColumns="False" IsReadOnly="True"
                  HeadersVisibility="Column" CanUserAddRows="False"
                  LoadingRow="ProductsGrid_LoadingRow"
                  FontFamily="{StaticResource AppFont}">
            <DataGrid.Columns>
                <DataGridTemplateColumn Header="Фото" Width="90">
                    <DataGridTemplateColumn.CellTemplate>
                        <DataTemplate>
                            <Image Source="{Binding PhotoFullPath}" Height="70" Stretch="Uniform"/>
                        </DataTemplate>
                    </DataGridTemplateColumn.CellTemplate>
                </DataGridTemplateColumn>
                <DataGridTextColumn Header="Артикул" Binding="{Binding Article}" Width="80"/>
                <DataGridTextColumn Header="Наименование" Binding="{Binding ProductName}" Width="150"/>
                <DataGridTextColumn Header="Категория" Binding="{Binding CategoryName}" Width="100"/>
                <DataGridTextColumn Header="Описание" Binding="{Binding Description}" Width="150"/>
                <DataGridTextColumn Header="Производитель" Binding="{Binding ManufacturerName}" Width="110"/>
                <DataGridTextColumn Header="Поставщик" Binding="{Binding SupplierName}" Width="110"/>
                <DataGridTemplateColumn Header="Цена" Width="130">
                    <DataGridTemplateColumn.CellTemplate>
                        <DataTemplate>
                            <StackPanel Orientation="Horizontal">
                                <TextBlock Text="{Binding Price, StringFormat={}{0:F2} ₽}"
                                           TextDecorations="Strikethrough" Foreground="Red" Margin="0,0,5,0"
                                           Visibility="{Binding HasDiscount, Converter={StaticResource BoolToVis}}"/>
                                <TextBlock Foreground="Black">
                                    <TextBlock.Style>
                                        <Style TargetType="TextBlock">
                                            <Setter Property="Text" Value="{Binding Price, StringFormat={}{0:F2} ₽}"/>
                                            <Style.Triggers>
                                                <DataTrigger Binding="{Binding HasDiscount}" Value="True">
                                                    <Setter Property="Text" Value="{Binding FinalPrice, StringFormat={}{0:F2} ₽}"/>
                                                </DataTrigger>
                                            </Style.Triggers>
                                        </Style>
                                    </TextBlock.Style>
                                </TextBlock>
                            </StackPanel>
                        </DataTemplate>
                    </DataGridTemplateColumn.CellTemplate>
                </DataGridTemplateColumn>
                <DataGridTextColumn Header="Ед. изм." Binding="{Binding UnitMeasure}" Width="70"/>
                <DataGridTextColumn Header="На складе" Binding="{Binding QuantityStock}" Width="80"/>
                <DataGridTextColumn Header="Скидка %" Binding="{Binding Discount}" Width="80"/>
            </DataGrid.Columns>
        </DataGrid>
    </Grid>
</UserControl>
```

---

## Код: Views/ProductsView.xaml.cs

```csharp
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using BookStoreApp.Data;

namespace BookStoreApp.Views;

public partial class ProductsView : UserControl
{
    public ProductsView()
    {
        InitializeComponent();
        LoadData();
    }

    private void LoadData()
    {
        try
        {
            ProductsGrid.ItemsSource = DatabaseHelper.GetProducts()
                .Select(ProductRowView.From)
                .ToList();
        }
        catch (Exception ex)
        {
            MessageBox.Show("Не удалось загрузить товары:\n" + ex.Message,
                "Ошибка", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    private void ProductsGrid_LoadingRow(object sender, DataGridRowEventArgs e)
    {
        if (e.Row.Item is not ProductRowView item) return;

        if (item.IsOutOfStock)
            e.Row.Background = Brushes.LightGray;
        else if (item.IsHighDiscount)
            e.Row.Background = (Brush)FindResource("DiscountBg");
        else
            e.Row.Background = Brushes.White;
    }
}
```

---

## BookStoreApp.csproj (фрагмент)

```xml
<PropertyGroup>
  <ApplicationIcon>import\icon.ico</ApplicationIcon>
</PropertyGroup>
<ItemGroup>
  <Content Include="import\**\*">
    <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
  </Content>
  <Resource Include="logo.png" />
</ItemGroup>
<ItemGroup>
  <PackageReference Include="FirebirdSql.Data.FirebirdClient" Version="10.3.4" />
</ItemGroup>
```

Удали или закомментируй `StartupUri="MainWindow.xaml"` в стандартном шаблоне — используется `LoginWindow` в `App.xaml`.

---

## Тестовые учётные записи

| Роль | Логин | Пароль |
|------|-------|--------|
| Администратор | `94d5ous@gmail.com` | `uzWC67` |
| Менеджер | `ptec8ym@yahoo.com` | `LdNyos` |
| Клиент | `yzls62@outlook.com` | `JlFRCZ` |

---

## Правила отображения товаров

| Условие | Действие |
|---------|----------|
| `Discount > 25` | фон строки `#23E1EF` |
| `Discount > 0` | старая цена красная, перечёркнута; рядом итоговая чёрная |
| `QuantityStock == 0` | строка серая (`LightGray`) |
| Нет файла фото | `import\picture.png` |

---

## Блок-схема (кратко для PDF)

```
[Старт] → [Окно входа]
    → (Гость?) → [Список товаров]
    → (Логин/пароль) → (Верно?) → Нет → сообщение → вход
                      → Да → (Роль?) → экран с меню + товары
    → [Выйти] → [Окно входа]
```

---

## Чек-лист модуля 2

- [ ] PDF блок-схема
- [ ] Вход, гость, 3 роли, ФИО, выход
- [ ] Товары из БД, стиль Comic Sans MS
- [ ] Подсветка скидки / нет на складе / цена
- [ ] docx со скриншотами
- [ ] Приложение не падает
