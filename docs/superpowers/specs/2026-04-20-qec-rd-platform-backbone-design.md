# QEC-RD 平台统一主干设计

日期：2026-04-20

## 1. 背景与目标

QEC-RD-Software 的长期目标是成为一个面向量子纠错科研与工程的全栈研发基座，覆盖从码与电路构造、真实噪声建模、高效模拟、DEM 提取、解码分析到后续 FTQC 估计的完整工作流。

当前仓库已经具备一个基于 `stim` 的 Phase 0 最小闭环，但距离“统一主干 + 本地科研内核”仍有明显差距。本设计的目的不是直接实现完整平台，而是为下一阶段定义一个稳定、可扩展、可逐步落地的统一主干。

本设计聚焦第一阶段目标：

- 构建 `qec_rd` 自有的统一对象模型与流程主链。
- 以 `stim` 作为第一阶段唯一底层执行底座。
- 在 `qec_rd` 内部逐步吸收和重建 DeltaKit 的本地科研内核基本能力。
- 支持两类一等入口：平台内建 code 电路生成，以及外部电路导入。
- 将 rotated surface code、unrotated surface code、toric code 纳入平台内建 code 范围。
- 允许用户定义任意 code，尤其是任意 CSS code，并基于 code 信息生成简单的 stabilizer measurement circuit。
- 将 MWPM 与 BP+OSD 纳入实现与验收目标，但解码算法本体依赖常用外部包，不在仓库内自研实现。
- 允许用户接入自定义 decoder，并使其能够走完整的端到端主链，而不是只能做孤立的离线调用。

## 2. 第一阶段设计边界

### 2.1 第一阶段纳入范围

- 基于 `stim` 的电路生成、导入、执行与采样。
- 统一的核心对象链：
  `CodeSpec -> CircuitArtifact -> DemArtifact -> DecodingGraph -> SyndromeBatch -> DecodeResult -> AnalysisReport`
- 平台内建支持 rotated surface code、unrotated surface code、toric code。
- 支持用户给定 code 信息，尤其是 CSS code 信息，并生成简单 stabilizer measurement circuit。
- 仅支持 Stim 可执行的 Pauli 类噪声模型表达与注入。
- 从电路提取 DEM 并构建标准解码图。
- 至少一条 MWPM 解码路径。
- 至少一条 BP+OSD 解码路径。
- 支持自定义 decoder 接入到统一 `run_decoder(...) -> DecodeResult -> AnalysisReport` 主链。
- 基础逻辑错误率、批量统计和基础实验分析。
- 面向未来新 code 与新电路研究的导入型工作流。

### 2.2 第一阶段明确不纳入范围

- 多 provider 机制。
- 将 DeltaKit 或 TensorQEC 作为运行时 provider 接入主链。
- 云端 API、认证、远程实验执行。
- notebook 工作流本身。
- 完整硬件控制、编译部署与实验编排。
- TensorQEC 的实现级集成。
- 非 Pauli 噪声模型。
- 全量复刻 DeltaKit Explorer 的外围可视化和高级分析生态。
- 自研 MWPM、BP+OSD 等解码算法本体。

## 3. 总体架构

第一阶段采用“平台主干 + Stim 唯一底座”的结构，不引入多后端抽象。DeltaKit 和 TensorQEC 在这一阶段是设计参考来源，不作为运行时实现组件。

### 3.1 分层结构

- `qec_rd.core`
  平台级核心对象、类型、异常和结果模型。
- `qec_rd.kernel.circuit`
  电路与码实验内核。
- `qec_rd.kernel.graph`
  DEM 与解码图内核。
- `qec_rd.kernel.decode`
  解码流程内核。
- `qec_rd.kernel.analysis`
  分析内核。
- `qec_rd.adapters.stim`
  与 `stim` 的底层桥接和格式适配。
- `qec_rd.api`
  薄 API 入口。

### 3.2 依赖方向

- `qec_rd.api` 可以依赖 `qec_rd.kernel.*` 与 `qec_rd.core`
- `qec_rd.kernel.*` 可以依赖 `qec_rd.core` 与 `qec_rd.adapters.stim`
- `qec_rd.adapters.stim` 可以依赖 `qec_rd.core`
- `qec_rd.core` 不依赖其他业务包

### 3.3 架构约束

- 第一阶段所有可执行闭环都仅依赖 `stim` 作为底层执行能力。
- `kernel.graph`、`kernel.decode`、`kernel.analysis` 的公开输入输出不能直接暴露裸 `stim.Circuit` 或裸 `stim.DetectorErrorModel`。
- DeltaKit 是功能对标对象，不是第一阶段的运行时依赖主角。
- 自定义能力的开放点应建立在平台标准对象之上，而不是绕开 `qec_rd` 主干直接传递任意底层对象。
- Stage 1 的 DEM 提取与图构建逻辑应固定为平台内置行为，不作为用户可自定义扩展点开放。

## 4. 包结构与职责

### 4.1 `qec_rd.core`

该包承载平台的统一语义，至少包含以下内容：

- `codes.py`
  定义 `CodeSpec`
- `artifacts.py`
  定义 `CircuitArtifact`、`DemArtifact`、`DecodingGraph`
- `noise.py`
  定义 `NoiseModel`
- `results.py`
  定义 `SyndromeBatch`、`DecodeResult`、`AnalysisReport`
- `types.py`
  定义公共类型、协议、异常基类

### 4.2 `qec_rd.adapters.stim`

该包只承担与 `stim` 的桥接，不承载平台分析逻辑：

- 构建或加载 `stim.Circuit`
- 从 Stim 电路提取 DEM
- 执行 detector / measurement sampling
- 在 Stim 原生对象与平台标准对象之间做转换

### 4.3 `qec_rd.kernel.circuit`

负责电路与码实验内核能力：

- 从 `CodeSpec` 生成基础 code family 电路
- 从 rotated surface code、unrotated surface code、toric code 的结构化定义生成电路
- 从用户提供的任意 CSS code 信息生成简单 stabilizer measurement circuit
- 导入并包装外部电路
- 电路基础检查
- 注释、坐标、logical observable、detector 元信息整理
- 噪声注入编排

### 4.4 `qec_rd.kernel.graph`

负责从电路或 DEM 走向标准解码结构：

- DEM 解析
- detector、observable、边界和注释语义抽取
- 标准解码图构建
- 边权、坐标和窗口化等图处理

### 4.5 `qec_rd.kernel.decode`

负责解码调用流程，但不自研解码算法：

- 标准化解码输入
- 对接外部解码器
- 对接用户自定义 decoder
- 统一解码结果输出
- 解码失败、参数与异常标准化

### 4.6 `qec_rd.kernel.analysis`

负责基础研究分析：

- logical error rate
- 批量统计
- 参数扫描结果聚合
- 基础误差分布和误差预算骨架

### 4.7 `qec_rd.api`

保持薄而稳定，只暴露常用本地科研入口：

- `build_circuit(...)`
- `load_circuit(...)`
- `extract_dem(...)`
- `build_decoding_graph(...)`
- `sample_syndromes(...)`
- `run_decoder(...)`
- `analyze_results(...)`

## 5. 核心对象定义原则

### 5.1 实验意图对象

- `CodeSpec`
  用于表达码族、distance、rounds、logical_basis、schedule、layout 等实验定义。
- `NoiseModel`
  用于表达 Stim 可执行的 Pauli 类噪声、基础现象学噪声与基础物理噪声参数。

这类对象描述“要做什么实验”，不承载运行结果。

### 5.2 执行工件对象

- `CircuitArtifact`
  表达统一电路工件，是后续主链的标准电路入口。
- `DemArtifact`
  表达统一 DEM 工件和其解释信息。
- `DecodingGraph`
  表达标准解码图或预留超图结构的解码工件。

### 5.3 运行数据对象

- `SyndromeBatch`
  承接 dets、meas、obs 等批量运行数据，并记录 shots、seed、采样来源与配置。

### 5.4 结果对象

- `DecodeResult`
  记录 logical flips 预测、失败统计、解码器信息和解码配置。
- `AnalysisReport`
  记录逻辑错误率、参数扫描、统计置信信息和基础分析结论。

### 5.5 对象约束

- 核心对象必须可导出为结构化数据，至少达到 dict/JSON-friendly 水平。
- 核心对象允许内部缓存 Stim 原生对象，但不将 Stim 原生对象作为主干公开语义。
- 必须严格区分“意图”“工件”“运行数据”“结果”。
- 对象构造后应保持语义稳定，优先不可变或半不可变。
- 每个关键对象必须携带最小必要来源元数据。

## 6. `CircuitArtifact` 的双入口要求

`CircuitArtifact` 不能只服务“内建 code 生成”，还必须作为平台统一电路入口，允许外部电路导入。

### 6.1 生成型入口

- `build_circuit(CodeSpec, NoiseModel | None) -> CircuitArtifact`

### 6.2 导入型入口

- `load_circuit(source, format, metadata=...) -> CircuitArtifact`

第一阶段导入型入口至少支持：

- `stim.Circuit`
- `.stim` 文件

设计上必须为未来导入以下形式预留位置：

- 电路文本
- `.qasm` 文件
- OpenQASM 2 / OpenQASM 3 等格式

### 6.3 `CircuitArtifact` 最小建议元数据

- `source_kind`
  例如 `generated`、`stim_object`、`stim_file`、`qasm_file`
- `source_format`
  例如 `stim`、`openqasm2`、`openqasm3`
- `origin_metadata`
  原始文件、生成器、版本、导入参数等
- `code_spec`
  可选字段，不要求所有电路都可追溯回完整 `CodeSpec`
- `raw_handle`
  可选缓存底层对象，例如 `stim.Circuit`

## 7. 第一阶段端到端数据流

### 7.1 两条入口

- 生成型入口：
  `CodeSpec (+ NoiseModel) -> build_circuit(...) -> CircuitArtifact`
- 导入型入口：
  `stim.Circuit / .stim / 未来 qasm -> load_circuit(...) -> CircuitArtifact`

### 7.2 统一主链

一旦进入 `CircuitArtifact`，后续全部走同一主链：

- `extract_dem(CircuitArtifact) -> DemArtifact`
- `build_decoding_graph(DemArtifact) -> DecodingGraph`
- `sample_syndromes(CircuitArtifact, ...) -> SyndromeBatch`
- `run_decoder(DecodingGraph, SyndromeBatch, ...) -> DecodeResult`
- `analyze_results(...) -> AnalysisReport`

### 7.3 每一阶段的责任

- 电路进入阶段：
  统一生成和导入两种电路来源。
- DEM 提取阶段：
  将电路转为标准错误模型工件。
- 解码图阶段：
  将 DEM 转为统一解码结构。
- 采样阶段：
  将 Stim 运行数据标准化为 `SyndromeBatch`
- 解码阶段：
  将图与运行数据结合，输出统一解码结果。
- 分析阶段：
  将解码结果转为研究可解释指标。

## 8. 解码器策略

第一阶段必须纳入 MWPM 与 BP+OSD 两类解码路径，但不在仓库内自研其算法实现。

### 8.1 外部包约束

- MWPM 使用常用外部包 `pymatching`
- BP+OSD 优先使用常用外部包生态 `ldpc` / `bposd`

`qec_rd` 在这一阶段的职责是：

- 组织统一解码输入
- 将 `DecodingGraph` 与 `SyndromeBatch` 转换为外部包所需形式
- 标准化输出为 `DecodeResult`
- 处理参数、异常、结果聚合
- 为用户自定义 decoder 提供同样的标准输入输出契约

`qec_rd` 在这一阶段不承担：

- MWPM 算法实现
- BP+OSD 算法实现
- 将外部解码器源码复制进仓库主干

### 8.2 解码器接口原则

- MWPM 与 BP+OSD 应通过统一的高层解码入口使用
- 两类解码器应输出同一种 `DecodeResult`
- 两类解码器应参与同一套分析流程
- 自定义 decoder 也应通过同一高层入口接入，输入至少基于 `DecodingGraph` 与 `SyndromeBatch`，输出必须可归一化为 `DecodeResult`

## 8A. 可自定义扩展点

第一阶段虽然不引入多 backend/provider 机制，但仍应允许若干“平台内扩展点”，以支持科研探索中的自定义设计。

### 8A.1 必须开放的扩展点

- 电路入口
  支持平台生成与外部电路导入两类入口。
- 解码器入口
  支持标准外部包解码器与用户自定义 decoder。

### 8A.2 建议开放的扩展点

- `CodeSpec` 扩展
  允许后续增加新的 code family、schedule 参数和实验元数据，而不破坏现有主链；第一阶段至少覆盖 rotated surface、unrotated surface、toric 与用户定义 CSS code。
- `NoiseModel` 扩展
  允许后续增加更多 Stim 支持的 Pauli 类噪声参数与 hardware-calibrated 参数，但第一阶段不纳入非 Pauli 噪声。
- 运行数据入口
  虽然第一阶段以 Stim 采样为主，但 `SyndromeBatch` 应允许未来承接外部实验数据或硬件回流数据。
- 分析层
  允许后续在 `AnalysisReport` 上叠加 threshold sweep、error budget、resource estimation 等分析逻辑，而不改动前面的对象链。

### 8A.3 第一阶段不建议开放为自定义点的部分

- 底层执行 backend
  第一阶段仍固定为 `stim`。
- DEM 提取与图构建策略
  第一阶段固定为平台内置实现，不作为用户自定义扩展点。
- 任意 provider/plugin 机制
  第一阶段不引入通用插件系统，只保留清晰但轻量的扩展边界。

## 9. 第一阶段实施波次

### 波次 0：主干对象与目录定型

- 建立 `qec_rd.core` 基础对象骨架
- 建立 `kernel.*`、`adapters.stim`、`api` 目录结构
- 固定依赖方向和异常结构

### 波次 1：Stim 电路入口打通

- 实现 `build_circuit(...)`
- 实现 `load_circuit(...)`
- 支持 `stim.Circuit`
- 支持 `.stim` 文件
- 至少支持一个基础 code family 的 memory experiment

### 波次 2：DEM 与解码图主链打通

- 提取 `DemArtifact`
- 构建标准 `DecodingGraph`
- 固定图构建失败语义

### 波次 3：采样与 MWPM 解码闭环

- 实现 `SyndromeBatch`
- 接入 `pymatching`
- 输出标准 `DecodeResult`
- 形成第一条完整闭环

### 波次 4：BP+OSD 解码接入

- 接入 `ldpc` / `bposd` 生态
- 补齐统一解码适配
- 确保与 MWPM 共用同一对象链

### 波次 5：批量分析与稳定化

- 批量扫描与汇总
- `AnalysisReport` 稳定化
- 对象导出能力
- 生成型与导入型闭环测试
- MWPM 与 BP+OSD 双路径验收测试

## 10. 第一阶段验收标准

### 10.1 对象链验收

- 生成型入口和导入型入口都必须进入同一条标准对象链：
  `CircuitArtifact -> DemArtifact -> DecodingGraph -> SyndromeBatch -> DecodeResult -> AnalysisReport`

### 10.2 Stim 唯一底座验收

- 第一阶段所有闭环均仅依赖 `stim` 作为执行底座
- 运行时不依赖 DeltaKit 作为平台主链实现

### 10.3 DeltaKit 本地科研主链对标验收

第一阶段至少对齐以下本地科研能力类别：

- 电路生成/导入
- rotated surface、unrotated surface、toric 三类内建 code
- 用户定义 CSS code 到简单 stabilizer measurement circuit 的生成
- Stim 驱动采样
- DEM 与图构建
- 基础本地解码
- 基础结果分析

### 10.4 外部电路研究入口验收

- 平台必须接受外部 Stim 电路作为一等输入
- 平台不能要求所有电路都来自内建 `CodeSpec`

### 10.5 MWPM 验收

- 平台能够通过外部 `pymatching` 包完成 MWPM 解码
- 平台将结果统一收束为 `DecodeResult`

### 10.6 BP+OSD 验收

- 平台能够通过外部 `ldpc` / `bposd` 生态完成 BP+OSD 解码
- 平台将结果统一收束为 `DecodeResult`

### 10.7 解码器适配验收

- `qec_rd` 不复制 MWPM、BP+OSD 算法实现进入主干
- 解码器作为外部包适配使用，而不是内部重写

### 10.7A 自定义 decoder 验收

- 平台允许用户接入自定义 decoder，并通过统一高层入口参与主链
- 自定义 decoder 的输入至少基于 `DecodingGraph` 和 `SyndromeBatch`
- 自定义 decoder 的输出必须可收束为 `DecodeResult`
- 自定义 decoder 的结果必须能够继续进入 `AnalysisReport` 生成流程

### 10.8 薄 API 验收

- 使用者仅通过 `qec_rd.api` 的少量入口即可完成基础本地科研实验
- 使用者不必直接操作底层 Stim 原生对象

## 11. 第一阶段完成后的平台状态

如果本设计完成第一阶段实现，平台应达到以下状态：

- 不再只是一个单纯的 Stim demo
- 已拥有 `qec_rd` 自有的统一核心对象体系
- 已能够承接 DeltaKit 本地科研主链的基本能力
- 已支持内建 code 电路与外部 Stim 电路导入两条研究路径
- 已支持 MWPM 与 BP+OSD 两类常见本地解码路径
- 已为后续扩展更多 code family、噪声模型、TensorQEC 能力与工程能力留下稳定主干
