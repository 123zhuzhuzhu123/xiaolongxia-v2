import { ConfigProvider } from "antd";
import "antd/dist/reset.css";

export const metadata = {
  title: "小龙虾 V2",
  description: "数据驱动的内容智能中台",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif" }}>
        <ConfigProvider theme={{ token: { colorPrimary: "#f43f5e" } }}>
          {children}
        </ConfigProvider>
      </body>
    </html>
  );
}
