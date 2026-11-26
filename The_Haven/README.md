# The Haven Los Angeles

1. 解压 ZIP，打开 `The_Haven_Los_Angeles` 文件夹。
2. 双击 **Start Hotel.command**，默认浏览器会自动打开酒店首页。
3. 使用网站期间保留终端窗口。按 **Control+C** 可以停止网站。

项目已附带 Flask 及其依赖、SQLite 数据库和图片。启动使用 Mac 上已安装的 Python 3.10 或更新版本。终端也会显示本次启动的本地网址。

顶部 **Sign in** 可以选择 Customer、Staff 或 Manager。压缩包带有原项目数据库，可以用原来的账号登录。原项目预置的演示账号如下。

| 角色 | 用户名 | 演示密码 |
| --- | --- | --- |
| Customer | `customer` | `customer123` |
| Staff | `staff` | `staff123` |
| Manager | `manager` | `manager123` |

客户可在登录页创建账户。账单支付使用测试卡资料模拟。房型按晚标价，设施按小时标价，餐食和餐饮服务另计。随包附带的数据库保留原有订单和账单金额。经理报表使用 Chart.js，图表加载需要网络。页面图片均为本地 WebP。

## 定价参考

- 房型基础价为每晚 $229、$289、$399 和 $539，参考洛杉矶市中心四星酒店及当地同类客房、露台房和套房的公开报价。 [Expedia 市中心四星酒店](https://www.expedia.com/4Star-Downtown-Los-Angeles-Los-Angeles-Hotels.s40-n800058-0.Travel-Guide-Filter-Hotels) · [The Hollywood Roosevelt 房型与报价](https://www.suiteness.com/suites/united-states/california/los-angeles/the-hollywood-roosevelt)
- 餐厅按项目原有的场地预订模型计费。餐饮定价参考当地酒店餐厅菜单，桑拿与泡浴参考洛杉矶本地浴场。 [Café Fig 菜单](https://www.hotelfigueroa.com/wp-content/uploads/2026/01/All-Day-Menu-rev-11.21.pdf) · [Spa LA](https://spala.us/first-timer-guide)
- 会议室与活动厅的小时租金参考洛杉矶本地会议室和同等规模活动场地。 [Davinci 会议室](https://cdn.davincimeetingrooms.com/loc/us/california/los-angeles-meeting-rooms) · [Skyline Loft](https://www.peerspace.com/pages/listings/592521947095140a00a985c4)

## 图片制作

使用内置 ImageGen 为虚构的 The Haven 制作 14 张场景图。提示词如下。

<details>
<summary>查看 ImageGen 提示词</summary>

- **Terrace** — Wide landscape 3:2 editorial architecture photograph for the homepage of an original contemporary boutique hotel in Downtown Los Angeles at late golden hour. Camera at the edge of an elevated rooftop terrace looking out over a believable Downtown LA skyline, iconic but distant, warm stepped midrise buildings beyond, palms and olive trees, an inviting honey travertine terrace at bottom right with a cream linen sun lounger and subtle terra cotta accents. Strong horizon, restrained warm sunlit palette with subtle rusty red earth accents. Left side is a subtly darker open skyline with open space for a white headline overlaid later; architecture and terrace are concentrated on the right. Photoreal high-end travel magazine architectural photography. No people, no watermarks, brands, letters, text, borders, or typography. Do not depict a pool.
- **Rooms** — A seamless exactly 2 by 2 contact sheet of FOUR distinct edge-to-edge architectural interior photos of guest rooms in the same original contemporary Downtown Los Angeles boutique hotel. Outer aspect landscape 3:2, equal-size quadrants, hard cuts exactly at center horizontally and vertically, zero margins/gutters/labels/frames; each quadrant is an independent wide photograph with the furnishings fully contained in its own cell. Top left: bright inviting guestroom with TWO parallel queen beds, ivory bedding, upholstered broad headboards and walnut nightstand. Top right: corner studio with one king bed and clearly visible open private balcony overlooking downtown. Bottom left: executive one-bedroom suite emphasizing a separate intimate living area with sofa, bedroom visible beyond a sliding door. Bottom right: larger family suite with a sunny dining nook, sofa, pantry and city view. Consistent warm oak and muted rust textiles, stone cream walls, natural California daylight and softly contrasting deep warm browns. Photoreal editorial hotel photography. No text or people.
- **Dining** — A seamless exactly 2 by 2 contact sheet of FOUR distinct architectural interior photos in an original contemporary LA boutique hotel, landscape 3:2, equal-size quadrants, hard cuts at exact center in both directions, absolutely no margins/gutters/labels/frames. Top left: warm refined Japanese noodle bar with long light wood counter and subtle terracotta; top right: intimate Spanish tapas and wine room with walnut and aged brass, amber evening light; bottom left: morning sun and greenery in an elegant lobby coffee shop, ceramic cups and croissants discreetly on counter; bottom right: sophisticated seasonal Californian restaurant with green upholstery, contemporary warm pendant lights and softly set tables. Editorial photographic realism, tactile locally inspired materials, clean contemporary design. No people, text or branding.
- **Wellness and social spaces** — A seamless exactly 2 by 2 contact sheet of FOUR distinct interior architectural photos in an original contemporary Los Angeles boutique hotel, landscape 3:2, equal-size quadrants, hard cuts exactly at center in both directions, absolutely no margins/gutters/labels/frames. Top left: warm contemporary cedar sauna spa with slatted timber, soft lighting and stone soaking bath visible. Top right: boutique hotel fitness studio with modern cardio and strength equipment and an indoor squash court seen through glazing. Bottom left: moody yet inviting walnut social lounge with green upholstered seating and a recognizable chessboard on the low table. Bottom right: modern private boardroom for 18 with a large walnut conferencing table, warm minimalist seating, tall windows and flat wall display with blank screen. Photoreal modern hotel design, restrained earthy tones, highly credible material detail. No people, text, labels, brands.
- **Events** — Wide landscape 3:2 photoreal architecture editorial photograph of a stylish 300-person event hall in an original new contemporary boutique hotel in Downtown Los Angeles. View across the room to full-height city windows and warm slatted oak acoustic walls, an elegant modular reception or seated event setup with subtle warm pendant lights, soft ivory furnishings, spare plantings, stylish but credible for an upscale four-star urban hotel. Coherent modern California design palette with warm oak, cream stone, olive accents and warm daylight. Blank walls, no lettering, branding, people, or borders.

</details>
