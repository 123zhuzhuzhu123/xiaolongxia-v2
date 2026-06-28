"use client";

import { Card, Statistic, Row, Col } from "antd";
import { useEffect, useState } from "react";
import { fetchContents, fetchCreators } from "@/lib/api";

const PROJECT_ID = 2;

export default function DashboardPage() {
  const [contents, setContents] = useState([]);
  const [creators, setCreators] = useState([]);

  useEffect(() => {
    fetchContents(PROJECT_ID, 1000).then(setContents);
    fetchCreators(PROJECT_ID).then(setCreators);
  }, []);

  const totalLikes = contents.reduce((sum: number, c: any) => sum + (c.likes || 0), 0);
  const totalComments = contents.reduce((sum: number, c: any) => sum + (c.comments || 0), 0);

  return (
    <div>
      <h1>决策看板</h1>
      <Row gutter={16}>
        <Col span={6}>
          <Card><Statistic title="内容资产" value={contents.length} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="创作者" value={creators.length} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="总点赞" value={totalLikes} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="总评论" value={totalComments} /></Card>
        </Col>
      </Row>
    </div>
  );
}
