"use client";

import { useEffect, useState } from "react";
import {
  Button,
  Card,
  Col,
  Drawer,
  Modal,
  Row,
  Select,
  Spin,
  Statistic,
  Table,
  Tag,
  Typography,
  message,
} from "antd";
import {
  fetchContents,
  fetchCopyDrafts,
  fetchSkus,
  generateCopy,
  generateStoryboard,
  scoreCopyVersion,
  selectCopyVersion,
} from "@/lib/api";

const PROJECT_ID = 2;
const { Title, Text, Paragraph } = Typography;

export default function CopywriterPage() {
  const [contents, setContents] = useState<any[]>([]);
  const [drafts, setDrafts] = useState<any[]>([]);
  const [skus, setSkus] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [generatingFor, setGeneratingFor] = useState<number | null>(null);
  const [selectedSku, setSelectedSku] = useState<number | null>(null);

  const [scoreModal, setScoreModal] = useState<{ open: boolean; data: any }>({
    open: false,
    data: null,
  });
  const [storyDrawer, setStoryDrawer] = useState<{ open: boolean; data: any }>({
    open: false,
    data: null,
  });

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [c, d, s] = await Promise.all([
        fetchContents(PROJECT_ID, 100),
        fetchCopyDrafts(PROJECT_ID),
        fetchSkus(PROJECT_ID),
      ]);
      setContents(c);
      setDrafts(d);
      setSkus(s);
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerate(content: any) {
    setGeneratingFor(content.id);
    try {
      await generateCopy(content.id, PROJECT_ID, selectedSku);
      message.success("文案生成成功");
      const d = await fetchCopyDrafts(PROJECT_ID);
      setDrafts(d);
    } catch (e: any) {
      message.error(e.response?.data?.detail || "生成失败");
    } finally {
      setGeneratingFor(null);
    }
  }

  async function handleScore(version: any) {
    const hide = message.loading("正在评分...", 0);
    try {
      const res = await scoreCopyVersion(version.id);
      setScoreModal({ open: true, data: res });
      const d = await fetchCopyDrafts(PROJECT_ID);
      setDrafts(d);
    } catch (e: any) {
      message.error(e.response?.data?.detail || "评分失败");
    } finally {
      hide();
    }
  }

  async function handleStoryboard(version: any) {
    const hide = message.loading("正在生成分镜...", 0);
    try {
      const res = await generateStoryboard(version.id);
      setStoryDrawer({ open: true, data: res });
    } catch (e: any) {
      message.error(e.response?.data?.detail || "分镜生成失败");
    } finally {
      hide();
    }
  }

  async function handleSelect(version: any) {
    try {
      await selectCopyVersion(version.id);
      message.success("已选择该版本");
      const d = await fetchCopyDrafts(PROJECT_ID);
      setDrafts(d);
    } catch (e: any) {
      message.error(e.response?.data?.detail || "选择失败");
    }
  }

  const contentColumns = [
    {
      title: "标题",
      dataIndex: "title",
      key: "title",
      ellipsis: true,
      render: (v: string) => v || "（无标题）",
    },
    {
      title: "点赞",
      dataIndex: "likes",
      key: "likes",
      width: 80,
      render: (v: number) => v || 0,
    },
    {
      title: "生成文案",
      key: "action",
      width: 240,
      render: (_: any, record: any) => (
        <Button
          type="primary"
          size="small"
          loading={generatingFor === record.id}
          onClick={() => handleGenerate(record)}
        >
          生成文案
        </Button>
      ),
    },
  ];

  return (
    <div>
      <h1>内容生产</h1>
      <Row gutter={16}>
        <Col span={10}>
          <Card
            title="选择素材"
            extra={
              <Select
                placeholder="选择主推 SKU（可选）"
                style={{ width: 180 }}
                allowClear
                onChange={(v) => setSelectedSku(v || null)}
              >
                {skus.map((s: any) => (
                  <Select.Option key={s.id} value={s.id}>
                    {s.sku_name}
                  </Select.Option>
                ))}
              </Select>
            }
          >
            <Table
              rowKey="id"
              loading={loading}
              dataSource={contents}
              columns={contentColumns}
              pagination={{ pageSize: 8 }}
              size="small"
            />
          </Card>
        </Col>

        <Col span={14}>
          <Card title="文案草稿">
            {drafts.length === 0 ? (
              <Text type="secondary">暂无文案草稿，请从左侧选择素材生成</Text>
            ) : (
              drafts.map((draft: any) => (
                <Card
                  key={draft.id}
                  size="small"
                  style={{ marginBottom: 16 }}
                  title={
                    <div>
                      <Tag color="blue">{draft.platform}</Tag>
                      <Text ellipsis style={{ maxWidth: 400 }}>
                        {draft.topic || "无主题"}
                      </Text>
                    </div>
                  }
                  extra={
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {new Date(draft.created_at).toLocaleString()}
                    </Text>
                  }
                >
                  {draft.versions.map((v: any) => (
                    <div
                      key={v.id}
                      style={{
                        marginBottom: 16,
                        padding: 12,
                        borderRadius: 8,
                        background: v.selected ? "#fff2f0" : "#f8fafc",
                        border: v.selected ? "1px solid #ffccc7" : "1px solid #e2e8f0",
                      }}
                    >
                      <div style={{ marginBottom: 8 }}>
                        <Tag>{v.formula_key}</Tag>
                        {v.selected && <Tag color="red">已选</Tag>}
                        {v.scores?.estimated_hook_rate && (
                          <Tag color="green">
                            预估转化率 {(v.scores.estimated_hook_rate * 100).toFixed(0)}%
                          </Tag>
                        )}
                        {v.quality_review?.overall && (
                          <Tag color="purple">综合分 {v.quality_review.overall}</Tag>
                        )}
                      </div>
                      <Title level={5}>{v.title}</Title>
                      <Paragraph>{v.body}</Paragraph>
                      {v.evidence?.selling_points?.length > 0 && (
                        <div style={{ marginBottom: 8 }}>
                          {v.evidence.selling_points.map((p: string) => (
                            <Tag key={p}>
                              {p}
                            </Tag>
                          ))}
                        </div>
                      )}
                      <div>
                        <Button size="small" onClick={() => handleScore(v)} style={{ marginRight: 8 }}>
                          质量评分
                        </Button>
                        <Button size="small" onClick={() => handleStoryboard(v)} style={{ marginRight: 8 }}>
                          生成分镜
                        </Button>
                        <Button size="small" type={v.selected ? "default" : "primary"} onClick={() => handleSelect(v)}>
                          {v.selected ? "已选择" : "选择该版本"}
                        </Button>
                      </div>
                    </div>
                  ))}
                </Card>
              ))
            )}
          </Card>
        </Col>
      </Row>

      <Modal
        open={scoreModal.open}
        title="文案质量评分"
        onCancel={() => setScoreModal({ open: false, data: null })}
        footer={null}
        width={700}
      >
        {scoreModal.data?.quality_review && (
          <div>
            <Row gutter={16}>
              <Col span={8}>
                <Statistic title="综合分" value={scoreModal.data.quality_review.overall} />
              </Col>
              <Col span={8}>
                <Statistic
                  title="是否通过"
                  value={scoreModal.data.quality_review.pass ? "通过" : "不通过"}
                />
              </Col>
            </Row>
            <Title level={5} style={{ marginTop: 16 }}>
              维度评分
            </Title>
            <Row gutter={16}>
              {Object.entries(scoreModal.data.quality_review.dimensions || {}).map(([k, v]: [string, any]) => (
                <Col span={8} key={k}>
                  <Card size="small" style={{ marginBottom: 8 }}>
                    <Statistic title={k} value={v} />
                  </Card>
                </Col>
              ))}
            </Row>
            <Title level={5} style={{ marginTop: 16 }}>
              优化建议
            </Title>
            <ul>
              {(scoreModal.data.quality_review.suggestions || []).map((s: string, i: number) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
        )}
      </Modal>

      <Drawer
        title="分镜脚本"
        open={storyDrawer.open}
        onClose={() => setStoryDrawer({ open: false, data: null })}
        styles={{ wrapper: { width: 720 } }}
      >
        {storyDrawer.data?.storyboard && (
          <div>
            <Text strong>总时长：{storyDrawer.data.storyboard.total_duration}s</Text>
            <Table
              rowKey="scene_no"
              size="small"
              dataSource={storyDrawer.data.storyboard.shots}
              pagination={false}
              columns={[
                { title: "镜号", dataIndex: "scene_no", width: 50 },
                { title: "景别", dataIndex: "shot_type", width: 80 },
                {
                  title: "画面/口播/备注",
                  render: (_: any, shot: any) => (
                    <div>
                      <Paragraph>
                        <Text strong>画面：</Text>
                        {shot.visual}
                      </Paragraph>
                      <Paragraph>
                        <Text strong>音频：</Text>
                        {shot.audio}
                      </Paragraph>
                      <Paragraph>
                        <Text strong>道具：</Text>
                        {(shot.props || []).join("、")}
                      </Paragraph>
                      {shot.note && (
                        <Paragraph type="secondary">
                          <Text strong>备注：</Text>
                          {shot.note}
                        </Paragraph>
                      )}
                    </div>
                  ),
                },
                { title: "时长", dataIndex: "duration_seconds", width: 60, render: (v: number) => `${v}s` },
              ]}
            />
          </div>
        )}
      </Drawer>
    </div>
  );
}
