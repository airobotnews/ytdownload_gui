README.md
# yt-dlp PyQt5 下载器

一个基于yt-dlp和PyQt5的图形界面视频下载工具，支持从YouTube和其他支持的网站下载视频。

## 功能特性

- 直观的图形用户界面
- 支持选择不同视频质量（最佳、720p、1080p）
- 实时下载进度显示
- 显示下载速度和文件大小信息
- 支持自定义下载目录
- 线程安全的下载过程
- 支持中断下载
- **新增功能：支持使用代理（VPN）**

## 系统要求

- Python 3.6 或更高版本
- PyQt5
- yt-dlp
- FFmpeg（用于视频处理）

## 安装依赖

在运行程序之前，请确保已安装所有必需的依赖库：

```bash
pip install pyqt5 yt-dlp
```

您还需要安装FFmpeg，可以从 [https://ffmpeg.org](https://ffmpeg.org) 下载并安装。

yt-dlp: https://github.com/yt-dlp/yt-dlp 

## 使用说明

1. 运行程序：
   
   ```bash
   python ytDownload_Qt5.py
   ```

2. 在"视频链接"输入框中粘贴您想要下载的视频URL。

3. 选择下载目录或使用默认的"downloads"目录。

4. 选择下载类型：
   
   - 最佳视频：下载最高质量的视频
   - 720p 视频：下载720p分辨率的视频
   - 1080p 视频：下载1080p分辨率的视频

5. **代理设置（可选）**：
   
   - 勾选"使用代理"复选框以启用代理
   - 默认代理地址为 `http://127.0.0.1:8080`，可根据需要修改
   - 当勾选"使用代理"后，输入框将被锁定，防止意外修改
   - 取消勾选则不使用代理

6. 点击"开始下载"按钮开始下载。

7. 在下载过程中，您可以看到进度条、下载速度和已下载的文件大小。

## 代理（VPN）使用说明

本工具支持通过代理服务器访问受地理限制的视频内容，这对于使用VPN服务的用户特别有用。

### 代理设置方法

1. **配置代理地址**：
   - 在程序界面中找到"使用代理"复选框和代理地址输入框
   - 默认代理地址为 `http://127.0.0.1:8080`，这是最常见的本地代理配置
   - 如果您的VPN服务使用不同的端口（如1080、8081等），请修改该地址

2. **常见代理格式**：
   - HTTP代理：`http://127.0.0.1:8080`
   - SOCKS5代理：`socks5://127.0.0.1:1080`
   - 如果您使用的是Shadowsocks、V2Ray等工具，请参考相应软件的代理设置页面获取正确的代理地址

3. **启用代理**：
   - 勾选"使用代理"复选框以激活代理设置
   - 此时代理地址输入框会被锁定，避免在下载过程中意外更改

4. **测试代理连接**：
   - 可先尝试访问一些网页确认代理正常工作
   - 如果下载失败，检查代理地址是否正确以及VPN服务是否正在运行

### 常见VPN/代理软件的配置示例

#### 1. Clash for Windows
- 默认HTTP代理端口：`7890`
- 代理地址：`http://127.0.0.1:7890`

#### 2. ShadowsocksR
- HTTP代理：`1087`，SOCKS5代理：`1080`
- 代理地址：`http://127.0.0.1:1087` 或 `socks5://127.0.0.1:1080`

#### 3. V2RayN
- HTTP代理：`10809`，SOCKS5代理：`10808`
- 代理地址：`http://127.0.0.1:10809` 或 `socks5://127.0.0.1:10808`

### 故障排除

- **无法连接到代理**：
  - 确认VPN服务正在运行
  - 检查代理地址和端口号是否正确
  - 确认代理协议（HTTP/SOCKS5）与实际服务匹配

- **下载速度变慢**：
  - VPN会增加网络延迟，可能导致下载速度下降
  - 尝试切换到地理位置较近的服务器
  - 检查本地网络和VPN服务器带宽

- **某些网站仍然无法访问**：
  - 某些网站可能检测并阻止常见的代理IP
  - 更换VPN服务器或尝试不同的代理协议

## 使用build_exe.bat打包Windows可执行文件

项目提供了[build_exe.bat](file:///c%3A/Users/QROBOT/Desktop/ytdownload_gui/build_exe.bat)批处理脚本来简化Windows下的打包过程。这个脚本会自动安装所需依赖并使用PyInstaller创建一个独立的可执行文件。

### 打包步骤

1. **准备文件**：
   - 确保项目根目录包含以下文件：
     - [ytDownload_Qt5.py](file:///c%3A/Users/QROBOT/Desktop/ytdownload_gui/ytDownload_Qt5.py)（主程序文件）
     - [requirements.txt](file:///c%3A/Users/QROBOT/Desktop/ytdownload_gui/requirements.txt)（依赖列表）
     - [download.png](file:///c%3A/Users/Administrator/Desktop/yt-dlb_qt5/download.png)（可选，程序图标）
     - [download.ico](file:///c%3A/Users/Administrator/Desktop/yt-dlb_qt5/download.ico)（可选，程序图标）
     - [build_exe.bat](file:///c%3A/Users/QROBOT/Desktop/ytdownload_gui/build_exe.bat)（打包脚本）

2. **运行打包脚本**：
   - 双击运行[build_exe.bat](file:///c%3A/Users/QROBOT/Desktop/ytdownload_gui/build_exe.bat)文件
   - 或者在命令提示符中执行：
   ```bash
   build_exe.bat
   ```

3. **等待打包完成**：
   - 脚本会自动安装依赖项并开始打包
   - 打包完成后，生成的可执行文件将位于`dist`目录中，文件名为`ytdownload_gui.exe`

### build_exe.bat功能说明

- 自动安装所需的Python包（yt-dlp、PyQt5等）
- 自动升级PyInstaller到最新版本
- 自动检测入口脚本（ytDownload_Qt5.py）
- 自动包含必要的资源文件（如图标）
- 自动检测并包含_ctypes和libffi相关的DLL文件（解决在某些Windows系统上的兼容性问题）
- 使用`--windowed`参数创建无控制台窗口的应用程序
- 生成的可执行文件位于`dist`目录中

### 自定义打包

如需自定义打包选项，可以直接编辑[build_exe.bat](file:///c%3A/Users/QROBOT/Desktop/ytdownload_gui/build_exe.bat)文件：

- 修改`NAME`变量来更改最终的可执行文件名
- 修改`ICON`变量来指定不同的图标文件
- 修改`ADD_DATA`变量来包含额外的数据文件

## 手动打包方法

如果您不想使用[build_exe.bat](file:///c%3A/Users/QROBOT/Desktop/ytdownload_gui/build_exe.bat)脚本，也可以手动使用PyInstaller进行打包：

### 安装PyInstaller

```bash
pip install pyinstaller
```

### 打包命令

要创建一个单独的可执行文件：

```bash
pyinstaller --onefile --windowed --icon=icon.ico --name="yt-dlp下载器" ytDownload_Qt5_2.py
```

参数说明：

- `--onefile`：将所有内容打包到一个单独的可执行文件中
- `--windowed`：不显示控制台窗口（适用于GUI应用）
- `--icon=icon.ico`：指定应用程序图标
- `--name`：指定生成的可执行文件名称

### 优化打包

如果您想要更小的文件大小和更快的启动速度，可以使用以下命令：

```bash
pyinstaller --onefile --windowed --icon=icon.ico --name="yt-dlp下载器" --add-data "icon.ico;." ytDownload_Qt5_2.py
```

打包后的可执行文件将位于 `dist` 目录中。

### 注意事项

- 打包过程可能需要几分钟时间
- 首次运行打包后的程序可能需要更长时间，因为需要解压和初始化
- 如果使用了`--onefile`参数，在程序运行时会临时解压到系统临时目录
- 确保在打包前将[icon.ico](file:///c%3A/Users/Administrator/Desktop/yt-dlb_qt5/icon.ico)文件放在与[ytDownload_Qt5_2.py](file:///c%3A/Users/Administrator/Desktop/yt-dlb_qt5/ytDownload_Qt5_2.py)相同的目录中

## 注意事项

- 请确保遵守相关网站的使用条款
- 请勿用于非法用途
- 某些网站可能有下载限制或需要登录
- 如果下载失败，请检查网络连接和视频链接是否有效

## 常见问题

### 无法下载视频

- 确保视频链接正确
- 检查网络连接
- 确保yt-dlp是最新版本：`yt-dlp -U`

### 视频质量选项无效

- 某些视频可能不提供所有质量选项
- 选择"最佳视频"通常会获得可用的最高质量

### 下载速度慢

- 网络连接速度可能影响下载速度
- 源服务器可能限制了下载速度
- 使用代理（VPN）可能会降低下载速度

### 打包后程序无法运行

- 确保系统安装了Microsoft Visual C++ Redistributable
- 检查是否包含必要的资源文件（如图标）
- 尝试使用`--debug`参数重新打包以查看错误信息

## 文件结构

- `ytDownload_Qt5_2.py` - 主程序文件
- `icon.ico` - 应用程序图标文件
- `downloads/` - 默认下载目录

## 许可证

本项目使用yt-dlp库，遵循其许可证协议。请参阅 yt-dlp 项目获取更多信息。

## 贡献

欢迎提交Issue和Pull Request来改进此工具。