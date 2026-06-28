"use client";

import { Layout, Menu, Typography } from "antd";
import {
  DashboardOutlined,
  SearchOutlined,
  DatabaseOutlined,
  EditOutlined,
} from "@ant-design/icons";
import Link from "next/link";
import { usePathname } from "next/navigation";

const { Sider, Content } = Layout;
const { Title } = Typography;

const menuItems = [
  { key: "/dashboard", icon: <DashboardOutlined />, label: <Link href="/dashboard">决策看板</Link> },
  { key: "/contents", icon: <DatabaseOutlined />, label: <Link href="/contents">内容资产</Link> },
  { key: "/analysis", icon: <SearchOutlined />, label: <Link href="/analysis">情报中心</Link> },
  { key: "/copywriter", icon: <EditOutlined />, label: <Link href="/copywriter">内容生产</Link> },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider theme="light" width={200}>
        <div style={{ padding: 16 }}>
          <Title level={5} style={{ margin: 0, color: "#f43f5e" }}>小龙虾 V2</Title>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[pathname]}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Content style={{ padding: 24, background: "#f8fafc" }}>{children}</Content>
      </Layout>
    </Layout>
  );
}
