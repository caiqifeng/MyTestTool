# 搭桥专家 - UE5 实现方案

## 项目概述

使用 Unreal Engine 5 重新实现《搭桥专家》游戏，利用 UE5 强大的物理引擎、蓝图系统和 Niagara 特效，打造更真实、视觉更震撼的桥梁建造体验。

## 技术栈选择

- **引擎版本**: Unreal Engine 5.3+
- **编程方式**: 蓝图 + C++ 混合（核心逻辑 C++，游戏流程蓝图）
- **物理引擎**: Chaos Physics（UE5 内置）
- **渲染管线**: Lumen 动态全局光照 + Nanite 虚拟几何体
- **UI 框架**: UMG（Unreal Motion Graphics）

## 项目结构

```
BridgeMaster/
├── Content/                          # 游戏资产
│   ├── Maps/                        # 关卡地图
│   │   ├── L_Level_01.umap          # 教学关卡
│   │   ├── L_Level_02.umap          # 峡谷关卡
│   │   └── L_Sandbox.umap           # 沙盒模式
│   ├── Blueprints/                  # 蓝图类
│   │   ├── GameModes/
│   │   │   ├── GM_BridgeMaster.uasset   # 游戏模式
│   │   │   └── GM_Sandbox.uasset
│   │   ├── Characters/
│   │   │   ├── BP_Vehicle.uasset    # 车辆蓝图
│   │   │   └── BP_Camera.uasset     # 相机控制
│   │   ├── Bridge/
│   │   │   ├── BP_BridgeComponent.uasset  # 桥梁组件基类
│   │   │   ├── BP_WoodBeam.uasset   # 木材组件
│   │   │   ├── BP_SteelBeam.uasset  # 钢筋组件
│   │   │   ├── BP_Concrete.uasset   # 混凝土组件
│   │   │   └── BP_Joint.uasset      # 连接点
│   │   ├── UI/
│   │   │   ├── W_MainMenu.uasset    # 主菜单
│   │   │   ├── W_BuildMode.uasset   # 建造模式UI
│   │   │   └── W_Results.uasset     # 结果界面
│   │   └── Controllers/
│   │       ├── PC_BridgeMaster.uasset  # 玩家控制器
│   │       └── PC_Spectator.uasset
│   ├── Materials/                   # 材质
│   │   ├── M_Wood.uasset
│   │   ├── M_Steel.uasset
│   │   └── M_Concrete.uasset
│   ├── StaticMeshes/                # 静态网格
│   │   ├── SM_WoodBeam.uasset
│   │   ├── SM_SteelBeam.uasset
│   │   └── SM_Vehicle.uasset
│   └── Physics/                     # 物理资产
│       └── PA_BridgeComponents.uasset
├── Source/                          # C++ 源代码
│   ├── BridgeMaster/                # 主模块
│   │   ├── BridgeMaster.Build.cs    # 构建脚本
│   │   ├── BridgeMaster.h
│   │   ├── BridgeMaster.cpp
│   │   ├── BridgeMasterGameModeBase.h
│   │   ├── BridgeMasterGameModeBase.cpp
│   │   ├── BridgeComponent.h        # 桥梁组件基类
│   │   ├── BridgeComponent.cpp
│   │   ├── VehiclePawn.h           # 车辆Pawn
│   │   ├── VehiclePawn.cpp
│   │   ├── BridgeManager.h         # 桥梁管理
│   │   ├── BridgeManager.cpp
│   │   ├── MaterialSystem.h        # 材料系统
│   │   └── MaterialSystem.cpp
│   └── BridgeMaster.Target.cs
└── Config/                          # 配置文件
    ├── DefaultGame.ini
    ├── DefaultEngine.ini
    └── DefaultInput.ini
```

## 核心系统设计

### 1. 物理桥梁系统

```cpp
// BridgeComponent.h
UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UBridgeComponent : public UPrimitiveComponent
{
    GENERATED_BODY()
    
public:
    UBridgeComponent();
    
    // 材料属性
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Material")
    FMaterialProperties MaterialProperties;
    
    // 受力计算
    UFUNCTION(BlueprintCallable, Category="Physics")
    float CalculateStress(FVector ForcePoint, FVector ForceDirection);
    
    // 断裂检测
    UFUNCTION(BlueprintCallable, Category="Physics")
    bool CheckFracture(float CurrentStress);
    
    // 成本计算
    UFUNCTION(BlueprintPure, Category="Economy")
    float GetCost() const { return MaterialProperties.CostPerMeter * GetComponentScale().X; }
    
protected:
    virtual void OnRegister() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, 
                               FActorComponentTickFunction* ThisTickFunction) override;
    
private:
    // 当前受力
    float CurrentStress;
    bool bIsBroken;
};
```

### 2. 材料属性数据结构

```cpp
// MaterialSystem.h
USTRUCT(BlueprintType)
struct FMaterialProperties
{
    GENERATED_BODY()
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString MaterialName;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    EMaterialType MaterialType;
    
    // 物理属性
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float Density;          // 密度 kg/m³
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float ElasticModulus;   // 弹性模量 Pa
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float YieldStrength;    // 屈服强度 Pa
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float MaxStress;        // 最大应力 Pa
    
    // 经济属性
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float CostPerMeter;     // 每米成本
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FLinearColor MaterialColor;
    
    // 网格引用
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    UStaticMesh* StaticMesh;
};
```

### 3. 车辆控制系统

```cpp
// VehiclePawn.h
UCLASS()
class AVehiclePawn : public APawn
{
    GENERATED_BODY()
    
public:
    AVehiclePawn();
    
    // 移动控制
    UFUNCTION(BlueprintCallable)
    void StartMoving();
    
    UFUNCTION(BlueprintCallable)
    void StopMoving();
    
    // 速度控制
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement")
    float MaxSpeed = 500.0f;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement")
    float Acceleration = 200.0f;
    
protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    
private:
    // 当前速度
    float CurrentSpeed;
    bool bIsMoving;
    
    // 物理组件
    UPrimitiveComponent* VehicleMesh;
};
```

## 蓝图实现关键点

### 1. 建造模式蓝图（BP_BuildModeController）

**事件图表**：
```
开始建造模式
├── 显示材料面板
├── 启用鼠标拖拽
├── 实时成本计算
└── 物理预览
```

**功能**：
- 材料拖拽放置
- 实时物理预览（绿色/红色指示器）
- 连接点自动吸附
- 撤销/重做功能

### 2. 桥梁管理器蓝图（BP_BridgeManager）

**职责**：
- 管理所有桥梁组件
- 计算整体结构稳定性
- 处理组件连接关系
- 统计总成本

### 3. 游戏模式蓝图（GM_BridgeMaster）

**游戏流程**：
```
开始游戏 → 建造模式 → 测试模式 → 结果评估 → 关卡完成
```

## 物理模拟设置

### Chaos Physics 配置

1. **桥梁组件物理体**：
   - 碰撞预设：`BridgeComponent`
   - 模拟生成：启用
   - 质量类型：`Mass`（计算质量）
   - 约束类型：`Fixed`、`Hinge`、`Cable`

2. **车辆物理体**：
   - 碰撞预设：`Vehicle`
   - 车轮设置：`Chaos Vehicle`
   - 悬挂系统：弹簧阻尼

3. **约束系统**：
   ```cpp
   // 创建焊接连接
   UPhysicsConstraintComponent* Constraint = NewObject<UPhysicsConstraintComponent>();
   Constraint->SetConstrainedComponents(ComponentA, NAME_None, ComponentB, NAME_None);
   Constraint->ConstraintActor1 = ComponentA->GetOwner();
   Constraint->ConstraintActor2 = ComponentB->GetOwner();
   Constraint->SetLinearXLimit(LCM_Locked, 0);
   Constraint->SetLinearYLimit(LCM_Locked, 0);
   Constraint->SetLinearZLimit(LCM_Locked, 0);
   ```

## UI/UX 设计

### 1. 建造模式界面（W_BuildMode）

```
+-----------------------------------+
| 材料面板 | 总成本: $XXX | 测试按钮 |
+-----------------------------------+
|                                   |
|           [游戏视图]              |
|                                   |
+-----------------------------------+
| 操作提示 | 当前材料: 木材         |
+-----------------------------------+
```

### 2. 材料面板组件
- 材料图标 + 名称 + 单价
- 拖拽到场景放置
- 库存数量显示

### 3. 结果界面（W_Results）
- 成功/失败标志
- 成本明细表
- 结构稳定性评分
- 全球排名对比

## 视觉效果

### 1. 材质系统
- **木材材质**：木纹法线贴图 + 粗糙度变化
- **钢筋材质**：金属度 + 划痕细节
- **混凝土材质**：表面颗粒 + 磨损边缘

### 2. 特效系统（Niagara）
- **断裂特效**：碎片飞溅 + 灰尘粒子
- **连接特效**：焊接火花
- **成功特效**：烟花 + 金币飞溅

### 3. 摄像机系统
- **建造视角**：自由飞行摄像机
- **测试视角**：跟随车辆 + 多角度切换
- **回放视角**：慢动作 + 镜头特写

## 音频设计

### 声音类别：
1. **UI声音**：按钮点击、材料选择
2. **建造声音**：材料放置、连接声音
3. **车辆声音**：引擎、轮胎摩擦
4. **结构声音**：咯吱声、断裂声
5. **环境声音**：风声、水流声

## 性能优化

### 1. LOD 系统
- 桥梁组件：3级LOD
- 车辆模型：2级LOD
- 地形：Nanite 处理

### 2. 物理优化
- 睡眠物理体
- 碰撞简化
- 异步物理计算

### 3. 渲染优化
- 遮挡剔除
- 实例化渲染
- Lumen 性能设置

## 关卡设计示例

### 关卡1：教学关
- **跨度**：10米
- **材料限制**：仅木材
- **目标成本**：< $200
- **教学要点**：基本拖拽、连接点、成本意识

### 关卡2：峡谷挑战
- **跨度**：30米
- **材料**：木材 + 钢筋
- **环境因素**：风力干扰
- **挑战**：悬索桥设计

### 关卡3：洪水关卡
- **跨度**：15米
- **挑战**：水流冲击桥墩
- **特殊机制**：动态水位变化

## 多平台支持

### PC 版：
- 键鼠操作精细控制
- 4K分辨率支持
- 超宽屏适配

### 移动版：
- 触摸拖拽 + 手势缩放
- 简化UI布局
- 性能模式选项

## 开发计划

### 第一阶段（1-2周）：核心原型
- 基本物理桥梁系统
- 车辆运动控制
- 建造模式基础

### 第二阶段（2-3周）：完整系统
- 材料系统 + 经济系统
- UI界面完整实现
- 多关卡设计

### 第三阶段（1-2周）：优化与内容
- 视觉效果提升
- 音效系统
- 性能优化

## 打包发布

### Windows 打包：
```bash
# 使用 Unreal Build Tool
UE4Editor.exe "Path/To/Project.uproject" -run=BuildCookRun -platform=Win64 -clientconfig=Shipping -build
```

### 移动端打包：
- Android：使用 Android Studio 配合
- iOS：需要 Mac + Xcode

## 项目文件下载

由于 UE5 项目文件较大，无法直接附件，请按以下步骤获取：

1. **创建新项目**：
   - 打开 UE5 Editor
   - 选择 "Games" → "Blank" 项目
   - 项目名称：`BridgeMaster`
   - 路径：自定义
   - 包含初学者内容：是

2. **导入核心文件**：
   - 下载提供的资产包（后续提供链接）
   - 将 `Content/` 文件夹覆盖项目内容
   - 将 `Source/` 文件夹复制到项目根目录

3. **编译项目**：
   - 右键点击 `.uproject` 文件 → "Generate Visual Studio project files"
   - 用 Visual Studio 打开 `.sln` 文件
   - 编译解决方案

## 技术支持

如遇到问题，请参考：
1. [UE5 官方文档](https://docs.unrealengine.com/)
2. Chaos Physics 文档
3. UMG UI 设计指南

---

**注意**：此方案为技术实现指南，实际开发需根据项目需求调整。建议先完成核心原型验证，再逐步添加高级功能。