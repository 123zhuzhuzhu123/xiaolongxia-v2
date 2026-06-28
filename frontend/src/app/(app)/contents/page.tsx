"use client";

import { Table, Tag, Card, Button, Modal, Spin, Statistic, Row, Col } from "antd";
import { useEffect, useState } from "react";
import { fetchContents } from "@/lib/api";
import { api } from "@/lib/api";

const PROJECT_ID = 2;

export default function ContentsPage() {
  const [contents, setContents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState("");
  const [modalLoading, setModalLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  useEffect(() => {
    setLoading(true);
    fetchContents(PROJECT_ID, 100)
      .then(setContents)
      .finally(() => setLoading(false));
  }, []);

  async function analyzeContent(content: any) {
    setModalOpen(true);
    setModalTitle(content.title || "内容分析");
    setModalLoading(true);
    setAnalysisResult(null);
    try {
      const [intent, viral] = await Promise.all([
        api.post("/analysis/comment-intent", { content_id: content.id }),
        api.post(`/analysis/viral-factors/${content.id}`),
      ]);
      setAnalysisResult({
        intent: intent.data,
        viral: viral.data,
      });
    } finally {
      setModalLoading(false);
    }
  }

  const columns = [
    { title: "平台", dataIndex: "platform", key: "platform", render: (v: string) => <Tag>{v}</Tag> },
    { title: "标题", dataIndex: "title", key: "title", ellipsis: true },
    { title: "点赞", dataIndex: "likes", key: "likes", sorter: (a: any, b: any) => (a.likes || 0) - (b.likes || 0) },
    { title: "评论", dataIndex: "comments", key: "comments" },
    { title: "分享", dataIndex: "shares", key: "shares" },
    {
      title: "评论样本",
      dataIndex: "comment_items",
      key: "comment_items",
      render: (v: any[]) => v?.length || 0,
    },
    {
      title: "操作",
      key: "action",
      render: (_: any, record: any) => (
        <Button size="small" onClick={() => analyzeContent(record)}>
          分析
        </Button>
      ),
    },
  ];

  return (
    <div>
      <h1>内容资产</h1>
      <Card>
        <Table
          rowKey="id"
          loading={loading}
          dataSource={contents}
          columns={columns}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        open={modalOpen}
        title={modalTitle}
        onCancel={() => setModalOpen(false)}
        footer={null}
        width={700}
      >
        {modalLoading ? (
          <Spin style={{ display: "block", margin: "40px auto" }} />
        ) : analysisResult ? (
          <div>
            <h3>评论意图分布</h3>
            <Row gutter={16}>
              {Object.entries(analysisResult.intent.intent_counts).map(([k, v]: [string, any]) => (
                <Col span={8} key={k}>
                  <Card size="small">
                    <Statistic title={k} value={v} />
                  </Card>
                </Col>
              ))}
            </Row>

            <h3 style={{ marginTop: 16 }}>情感分布</h3>
            <Row gutter={16}>
              {Object.entries(analysisResult.intent.sentiment_counts).map(([k, v]: [string, any]) => (
                <Col span={8} key={k}>
                  <Card size="small">
                    <Statistic title={k} value={v} />
                  </Card>
                </Col>
              ))}
            </Row>

            <h3 style={{ marginTop: 16 }}>爆款因子</h3>
            <Row gutter={16}>
              <Col span={8}>
                <Card size="small">
                  <Statistic title="互动分" value={analysisResult.viral.factors.engagement_score} />
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <Statistic title="收藏分" value={analysisResult.viral.factors.save_score} />
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <Statistic title="标题分" value={analysisResult.viral.factors.title_score} />
                </Card>
              </Col>
            </Row>
            <div style={{ marginTop: 12 }}>
              <strong>综合爆款分：</strong>
              <Tag color="red">{analysisResult.viral.factors.viral_score}</Tag>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
