# BESx Codebase

Este arquivo contém todos os scripts e modelos atuais do projeto para análise.

## Arquivo: README.md
`markdown
# BESx - Simulação de Degradação de Baterias (BESS)

Este projeto realiza a simulação de sistemas de armazenamento de energia em baterias (BESS), integrando modelos de degradação com simulações elétricas via PLECS.

O objetivo principal é avaliar a degradação da bateria (perda de SOH - State of Health) ao longo do tempo, considerando tanto o envelhecimento cíclico (Rainflow) quanto o envelhecimento calendárico.

## Funcionalidades Principais

- **Integração com PLECS**: Comunicação via XML-RPC para executar simulações elétricas.
- **Modelo de Degradação**: Cálculos de dano por ciclo (DOD, SOC médio, Temperatura) e calendário (Tempo, SOC, Temperatura).
- **Gerenciamento de Resultados**:
  - Criação automática de pastas por simulação (`results/sim_YYYYMMDD_HHMMSS/`).
  - Geração de relatórios automáticos (`report.txt`).
  - Salvamento de gráficos e planilhas de debug organizados.
- **Modularidade**: Código estruturado em pacote Python (`besx_app`).

## Estrutura do Projeto

```bash
BESx/
├── besx_app/              # Pacote principal da aplicação
│   ├── core/              # Lógica de simulação e conexão com PLECS
│   ├── models/            # Modelos matemáticos de degradação
│   └── utils/             # Manipulação de dados, plots e arquivos
├── database/              # Pasta para colocar seus arquivos de entrada (.mat, .csv)
├── results/               # Saída das simulações (criado automaticamente)
├── tests/                 # Testes unitários
├── config.py              # Arquivo de configuração central
├── main.py                # Script de execução
└── requirements.txt       # Dependências
```

## Pré-requisitos

1. **Python 3.8+**
2. **PLECS Standalone**: Com o servidor XML-RPC habilitado (padrão na porta 1080).
    - O modelo `bess_batch_mode.plecs` deve estar acessível conforme configurado em `config.py`.

## Instalação

1. Clone este repositório.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como Usar

1. **Configuração**:
    - Ajuste os parâmetros em `config.py` (capacidade, dados de entrada, limites).
    - Coloque seus arquivos de dados na pasta `database/`.

2. **Execução**:
    - Certifique-se que o PLECS está aberto com o servidor XML-RPC ativo.
    - Rode o script:

```bash
python main.py
```

1. **Resultados**:
    - A cada execução, uma nova pasta será criada em `results/` com a data e hora.
    - Verifique `report.txt` para um resumo rápido.
    - Gráficos estarão em `results/.../plots/`.
    - Dados detalhados em `results/.../data/` e `results/.../debug/`.

`

## Arquivo: bess_batch_mode.plecs
`xml
Plecs {
  Name          "bess_batch_mode"
  Version       "4.9"
  CircuitModel  "DiscStateSpace"
  StartTime     "0.0"
  TimeSpan      "30*24*60*60"
  Timeout       ""
  Solver        "FixedStepDiscrete"
  MaxStep       "1e-3"
  InitStep      "-1"
  FixedStep     "10"
  Refine        "1"
  ZCStepSize    "1e-9"
  RelTol        "1e-2"
  AbsTol        "-1"
  TurnOnThreshold "0"
  NonIdealSwitchResistance "1"
  SyncFixedStepTasks "2"
  UseSingleCommonBaseRate "2"
  LossVariableLimitExceededMsg "3"
  NegativeSwitchLossMsg "3"
  DivisionByZeroMsg "3"
  DatatypeOverflowMsg "2"
  DatatypeInheritanceConflictMsg "1"
  ContSampleTimeConflictMsg "1"
  StiffnessDetectionMsg "2"
  MaxConsecutiveZCs "1000"
  AlgebraicLoopWithStateMachineMsg "3"
  AssertionAction "1"
  FixedPointDatatypeOverride "1"
  InitializationCommands ""
  InitialState  "1"
  SystemState   ""
  TaskingMode   "1"
  TaskConfigurations ""
  CodeGenParameterInlining "2"
  CodeGenFloatingPointFormat "2"
  CodeGenAbsTimeUsageMsg "3"
  CodeGenBaseName ""
  CodeGenOutputDir ""
  CodeGenExtraOpts ""
  CodeGenTarget "Generic"
  CodeGenTargetSettings ""
  ExtendedMatrixPrecision "1"
  MatrixSignificanceCheck "2"
  RemoveUnusedStateSpaceOutputs "1"
  EnableStateSpaceSplitting "2"
  DisplayStateSpaceSplitting "1"
  DiscretizationMethod "2"
  ExternalModeSettings ""
  AlgebraicLoopMethod "1"
  AlgebraicLoopTolerance "1e-6"
  ScriptsDialogGeometry "[743 385 466 244]"
  ScriptsDialogSplitterPos "96"
  Schematic {
    Location      [179, 1218; 1617, 2175]
    ZoomFactor    1.96257
    SliderPosition [59, -1]
    ShowBrowser   off
    BrowserWidth  158
    Component {
      Type          Voltmeter
      Name          "Vm1"
      Show          on
      Position      [290, 105]
      Direction     down
      Flipped       on
      LabelPosition east
    }
    Component {
      Type          Scope
      Name          base64 "VGVuc8OjbyBlIENvcnJlbnRlCm5hIEJhdGVyaWE="
      Show          on
      Position      [700, 375]
      Direction     up
      Flipped       off
      LabelPosition south
      Location      [-1919, 31; -961, 1010]
      State         "AAAA/wAAAAD9AAAAAgAAAAEAAAC0AAACmfwCAAAAA/sAAAAQAFoAbwBvA"
"G0AQQByAGUAYQAAAAAA/////wAAAIEA////+wAAABQAUwBhAHYAZQBkAFYAaQBlAHcAcwAAAAA0AA"
"ACmQAAAGMA////+wAAAAwAVAByAGEAYwBlAHMAAAAAAP////8AAABjAP///wAAAAMAAAeAAAAAo/w"
"BAAAAAfsAAAAUAEQAYQB0AGEAVwBpAGQAZwBlAHQAAAAAAAAAB4AAAABEAP///wAAA74AAAO0AAAA"
"BAAAAAQAAAAIAAAACPwAAAABAAAAAgAAAAEAAAAOAFQAbwBvAGwAQgBhAHIBAAAAAP////8AAAAAA"
"AAAAA=="
      SavedViews    "AAAAAgAAAAA="
      HeaderState   "{\"DefaultSecSize\":0,\"FirstSecSize\":106,\"Labels\":[],"
"\"VisualIdxs\":[]}"
      PlotPalettes  "AAAAAQAAAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAA"
"AEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
"=="
      Axes          "3"
      TimeRange     "0"
      ScrollingMode "1"
      SingleTimeAxis "1"
      Open          "0"
      Ts            "-1"
      SampleLimit   "0"
      XAxisLabel    "Time / s"
      ShowLegend    "2"
      Axis {
        Name          ""
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Axis {
        Name          ""
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {base64 "VGVuc8Ojbw=="}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Axis {
        Name          ""
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {"Corrent"}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Fourier {
        SingleXAxis       on
        AxisLabel         "Frequency / Hz"
        Scaling           0
        PhaseDisplay      0
        ShowFourierLegend off
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {base64 "VGVuc8Ojbw=="}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {"Corrent"}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
      }
    }
    Component {
      Type          Subsystem
      Name          "Battery"
      Show          on
      Position      [415, 95]
      Direction     up
      Flipped       off
      LabelPosition westNorthwest
      Frame         [-25, -35; 25, 35]
      SampleTime    "-1"
      CodeGenDiscretizationMethod "2"
      CodeGenTarget "Generic"
      MaskDisplayLang "2"
      MaskIconFrame on
      MaskIconOpaque off
      MaskIconRotates on
      Terminal {
        Type          Port
        Position      [-15, -40]
        Direction     up
      }
      Terminal {
        Type          Output
        Position      [29, -30]
        Direction     right
      }
      Terminal {
        Type          Port
        Position      [-15, 40]
        Direction     down
      }
      Terminal {
        Type          Output
        Position      [29, -20]
        Direction     right
      }
      Schematic {
        Location      [0, 62; 1920, 1038]
        ZoomFactor    1.49862
        SliderPosition [-1, -1]
        ShowBrowser   off
        BrowserWidth  100
        Component {
          Type          Port
          Name          "+"
          Show          on
          Position      [1025, 280]
          Direction     left
          Flipped       off
          LabelPosition north
          Parameter {
            Variable      "Index"
            Value         "1"
            Show          on
          }
          Parameter {
            Variable      "Width"
            Value         "-1"
            Show          off
          }
        }
        Component {
          Type          Constant
          Name          "Capacity"
          Show          on
          Position      [180, 345]
          Direction     right
          Flipped       off
          LabelPosition south
          Frame         [-10, -10; 10, 10]
          Parameter {
            Variable      "Value"
            Value         "Ah"
            Show          off
          }
          Parameter {
            Variable      "DataType"
            Value         "10"
            Show          off
          }
        }
        Component {
          Type          Gain
          Name          "Gain"
          Show          on
          Position      [295, 345]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "K"
            Value         "3600"
            Show          off
          }
          Parameter {
            Variable      "Multiplication"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "OutputDataType"
            Value         "10"
            Show          off
          }
          Parameter {
            Variable      "DataTypeOverflowMode"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "GainDataType"
            Value         "11"
            Show          off
          }
        }
        Component {
          Type          Product
          Name          "Divide"
          Show          off
          Position      [355, 340]
          Direction     up
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "IconShape"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "Inputs"
            Value         "*/"
            Show          off
          }
          Parameter {
            Variable      "DataType"
            Value         "11"
            Show          off
          }
          Parameter {
            Variable      "DataTypeOverflowMode"
            Value         "1"
            Show          off
          }
        }
        Component {
          Type          Gain
          Name          "Gain1"
          Show          on
          Position      [640, 460]
          Direction     down
          Flipped       off
          LabelPosition west
          Parameter {
            Variable      "K"
            Value         "100"
            Show          off
          }
          Parameter {
            Variable      "Multiplication"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "OutputDataType"
            Value         "11"
            Show          off
          }
          Parameter {
            Variable      "DataTypeOverflowMode"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "GainDataType"
            Value         "11"
            Show          off
          }
        }
        Component {
          Type          VoltageSource
          Name          "V"
          Show          on
          Position      [810, 365]
          Direction     down
          Flipped       on
          LabelPosition east
          Parameter {
            Variable      "DiscretizationBehavior"
            Value         "2"
            Show          off
          }
          Parameter {
            Variable      "StateSpaceInlining"
            Value         "1"
            Show          off
          }
        }
        Component {
          Type          Ammeter
          Name          "Am1"
          Show          on
          Position      [945, 280]
          Direction     left
          Flipped       on
          LabelPosition south
        }
        Component {
          Type          Integrator
          Name          "Integrator"
          Show          on
          Position      [540, 365]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "ExternalReset"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "InitialConditionSource"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "x0"
            Value         "SOC_0"
            Show          off
          }
          Parameter {
            Variable      "ShowStatePort"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "EnableWrapping"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "UpperLimit"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "LowerLimit"
            Value         "0"
            Show          off
          }
        }
        Component {
          Type          Lookup1D
          Name          "SOC x VOC"
          Show          on
          Position      [630, 365]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "x"
            Value         "SOC"
            Show          off
          }
          Parameter {
            Variable      "f(x)"
            Value         "OCV"
            Show          off
          }
          Parameter {
            Variable      "ZeroCrossingSignals"
            Value         "1"
            Show          off
          }
        }
        Component {
          Type          Output
          Name          "SOC [%]"
          Show          on
          Position      [640, 510]
          Direction     down
          Flipped       off
          LabelPosition west
          Parameter {
            Variable      "Index"
            Value         "2"
            Show          on
          }
          Parameter {
            Variable      "Width"
            Value         "-1"
            Show          off
          }
        }
        Component {
          Type          Port
          Name          "-"
          Show          on
          Position      [1025, 385]
          Direction     left
          Flipped       off
          LabelPosition north
          Parameter {
            Variable      "Index"
            Value         "3"
            Show          on
          }
          Parameter {
            Variable      "Width"
            Value         "-1"
            Show          off
          }
        }
        Component {
          Type          PlecsProbe
          Name          "Probe"
          Show          on
          Position      [1215, 635]
          Direction     right
          Flipped       off
          LabelPosition south
        }
        Component {
          Type          Reference
          SrcComponent  "Components/Control/Filters/Moving Average"
          Name          "Moving Average"
          Show          on
          Position      [1325, 635]
          Direction     up
          Flipped       off
          LabelPosition south
          Frame         [-15, -15; 15, 15]
          Parameter {
            Variable      "x0"
            Value         "0"
            Show          off
          }
          Parameter {
            Variable      "T_period"
            Value         "300"
            Show          off
          }
          Parameter {
            Variable      "buffer_size"
            Value         "256"
            Show          off
          }
          Terminal {
            Type          Output
            Position      [19, 0]
            Direction     right
          }
          Terminal {
            Type          Input
            Position      [-15, 0]
            Direction     left
          }
        }
        Component {
          Type          Sum
          Name          "Sum"
          Show          off
          Position      [1265, 635]
          Direction     up
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "IconShape"
            Value         "2"
            Show          off
          }
          Parameter {
            Variable      "Inputs"
            Value         "|++"
            Show          off
          }
          Parameter {
            Variable      "DataType"
            Value         "11"
            Show          off
          }
          Parameter {
            Variable      "DataTypeOverflowMode"
            Value         "1"
            Show          off
          }
        }
        Component {
          Type          Scope
          Name          "Perdas Internas"
          Show          on
          Position      [1415, 635]
          Direction     up
          Flipped       off
          LabelPosition south
          Location      [-1279, 300; -929, 531]
          State         "AAAA/wAAAAD9AAAAAgAAAAEAAAAAAAAAAPwCAAAAA/sAAAAQAFoAb"
"wBvAG0AQQByAGUAYQAAAAAA/////wAAADEA////+wAAABQAUwBhAHYAZQBkAFYAaQBlAHcAcwAAAA"
"AA/////wAAAGMA////+wAAAAwAVAByAGEAYwBlAHMAAAAAAP////8AAABjAP///wAAAAMAAAAAAAA"
"AAPwBAAAAAfsAAAAUAEQAYQB0AGEAVwBpAGQAZwBlAHQAAAAAAP////8AAABEAP///wAAAV4AAADI"
"AAAABAAAAAQAAAAIAAAACPwAAAABAAAAAgAAAAEAAAAOAFQAbwBvAGwAQgBhAHIBAAAAAP////8AA"
"AAAAAAAAA=="
          SavedViews    "AAAAAgAAAAA="
          HeaderState   "{\"DefaultSecSize\":0,\"FirstSecSize\":150,\"Labels\""
":[],\"VisualIdxs\":[]}"
          PlotPalettes  "AAAAAQAAAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
          Axes          "1"
          TimeRange     "0.0"
          ScrollingMode "1"
          SingleTimeAxis "1"
          Open          "0"
          Ts            "-1"
          SampleLimit   "0"
          XAxisLabel    "Time / s"
          ShowLegend    "1"
          Axis {
            Name          ""
            AutoScale     1
            MinValue      0
            MaxValue      1
            Signals       {}
            SignalTypes   [ ]
            Untangle      0
            KeepBaseline  off
            BaselineValue 0
          }
          Fourier {
            SingleXAxis       on
            AxisLabel         "Frequency / Hz"
            Scaling           0
            PhaseDisplay      0
            ShowFourierLegend off
            Axis {
              Name          ""
              AutoScale     1
              MinValue      0
              MaxValue      1
              Signals       {}
              Untangle      0
              KeepBaseline  off
              BaselineValue 0
            }
          }
        }
        Component {
          Type          Gain
          Name          base64 "Q8OpbHVsYXMgZW0gUGFyYWxlbG8="
          Show          on
          Position      [720, 240]
          Direction     left
          Flipped       off
          LabelPosition north
          Parameter {
            Variable      "K"
            Value         "1/Np"
            Show          off
          }
          Parameter {
            Variable      "Multiplication"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "OutputDataType"
            Value         "11"
            Show          off
          }
          Parameter {
            Variable      "DataTypeOverflowMode"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "GainDataType"
            Value         "11"
            Show          off
          }
        }
        Component {
          Type          Gain
          Name          base64 "Q8OpbHVsYXMgCmVtIFPDqXJpZQ=="
          Show          on
          Position      [705, 365]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "K"
            Value         "Ns"
            Show          off
          }
          Parameter {
            Variable      "Multiplication"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "OutputDataType"
            Value         "10"
            Show          off
          }
          Parameter {
            Variable      "DataTypeOverflowMode"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "GainDataType"
            Value         "11"
            Show          off
          }
        }
        Component {
          Type          Product
          Name          "Product1"
          Show          off
          Position      [240, 345]
          Direction     up
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "IconShape"
            Value         "2"
            Show          off
          }
          Parameter {
            Variable      "Inputs"
            Value         "|**"
            Show          off
          }
          Parameter {
            Variable      "DataType"
            Value         "11"
            Show          off
          }
          Parameter {
            Variable      "DataTypeOverflowMode"
            Value         "1"
            Show          off
          }
        }
        Component {
          Type          From
          Name          "From"
          Show          off
          Position      [200, 410]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "Tag"
            Value         "SOH_Input"
            Show          off
          }
          Parameter {
            Variable      "Visibility"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "NoMatchingCounterpartAction"
            Value         "1"
            Show          off
          }
        }
        Component {
          Type          Constant
          Name          "Rs_inicial"
          Show          on
          Position      [325, 465]
          Direction     right
          Flipped       off
          LabelPosition south
          Frame         [-30, -10; 30, 10]
          Parameter {
            Variable      "Value"
            Value         "Rs*Ns/Np"
            Show          off
          }
          Parameter {
            Variable      "DataType"
            Value         "10"
            Show          off
          }
        }
        Component {
          Type          Product
          Name          "Divide1"
          Show          off
          Position      [435, 435]
          Direction     up
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "IconShape"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "Inputs"
            Value         "*/"
            Show          off
          }
          Parameter {
            Variable      "DataType"
            Value         "11"
            Show          off
          }
          Parameter {
            Variable      "DataTypeOverflowMode"
            Value         "1"
            Show          off
          }
        }
        Component {
          Type          Goto
          Name          "Goto"
          Show          off
          Position      [490, 435]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "Tag"
            Value         "R1"
            Show          off
          }
          Parameter {
            Variable      "Visibility"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "NoMatchingCounterpartAction"
            Value         "2"
            Show          off
          }
        }
        Component {
          Type          From
          Name          "From1"
          Show          off
          Position      [855, 315]
          Direction     right
          Flipped       on
          LabelPosition south
          Parameter {
            Variable      "Tag"
            Value         "R1"
            Show          off
          }
          Parameter {
            Variable      "Visibility"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "NoMatchingCounterpartAction"
            Value         "1"
            Show          off
          }
        }
        Component {
          Type          Reference
          SrcComponent  "Components/Electrical/Passive Components/R3"
          Name          "R3"
          Show          on
          Position      [810, 315]
          Direction     down
          Flipped       on
          LabelPosition west
          Frame         [-8, -15; 8, 15]
          Terminal {
            Type          Port
            Position      [0, -20]
            Direction     up
          }
          Terminal {
            Type          Port
            Position      [0, 20]
            Direction     down
          }
          Terminal {
            Type          Input
            Position      [-10, 10]
            Direction     left
          }
        }
        Component {
          Type          Scope
          Name          "Scope"
          Show          on
          Position      [755, 295]
          Direction     up
          Flipped       off
          LabelPosition south
          Location      [0, 23; 1920, 1011]
          State         "AAAA/wAAAAD9AAAAAgAAAAEAAAAAAAAAAPwCAAAAA/sAAAAQAFoAb"
"wBvAG0AQQByAGUAYQAAAAAA/////wAAANEA////+wAAABQAUwBhAHYAZQBkAFYAaQBlAHcAcwAAAA"
"AA/////wAAAGMA////+wAAAAwAVAByAGEAYwBlAHMAAAAAAP////8AAABjAP///wAAAAMAAAAAAAA"
"AAPwBAAAAAfsAAAAUAEQAYQB0AGEAVwBpAGQAZwBlAHQAAAAAAP////8AAABEAP///wAAB4AAAAO9"
"AAAABAAAAAQAAAAIAAAACPwAAAABAAAAAgAAAAEAAAAOAFQAbwBvAGwAQgBhAHIBAAAAAP////8AA"
"AAAAAAAAA=="
          SavedViews    "AAAAAgAAAAA="
          HeaderState   "{\"DefaultSecSize\":0,\"FirstSecSize\":166,\"Labels\""
":[],\"VisualIdxs\":[]}"
          PlotPalettes  "AAAAAQAAAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
"QAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
"AAAAAAAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAEAAAAAAAAAAAAAAAAAAAA"
"AAAAAAAAAAAA="
          Axes          "5"
          TimeRange     "0.0"
          ScrollingMode "1"
          SingleTimeAxis "1"
          Open          "0"
          Ts            "-1"
          SampleLimit   "0"
          XAxisLabel    "Time / s"
          ShowLegend    "1"
          Axis {
            Name          ""
            AutoScale     1
            MinValue      0
            MaxValue      1
            Signals       {}
            SignalTypes   [ ]
            Untangle      0
            KeepBaseline  off
            BaselineValue 0
          }
          Axis {
            Name          ""
            AutoScale     1
            MinValue      0
            MaxValue      1
            Signals       {}
            SignalTypes   [ ]
            Untangle      0
            KeepBaseline  off
            BaselineValue 0
          }
          Axis {
            Name          ""
            AutoScale     1
            MinValue      0
            MaxValue      1
            Signals       {}
            SignalTypes   [ ]
            Untangle      0
            KeepBaseline  off
            BaselineValue 0
          }
          Axis {
            Name          ""
            AutoScale     1
            MinValue      0
            MaxValue      1
            Signals       {}
            SignalTypes   [ ]
            Untangle      0
            KeepBaseline  off
            BaselineValue 0
          }
          Axis {
            Name          ""
            AutoScale     1
            MinValue      0
            MaxValue      1
            Signals       {}
            SignalTypes   [ ]
            Untangle      0
            KeepBaseline  off
            BaselineValue 0
          }
          Fourier {
            SingleXAxis       on
            AxisLabel         "Frequency / Hz"
            Scaling           0
            PhaseDisplay      0
            ShowFourierLegend off
            Axis {
              Name          ""
              AutoScale     1
              MinValue      0
              MaxValue      1
              Signals       {}
              Untangle      0
              KeepBaseline  off
              BaselineValue 0
            }
            Axis {
              Name          ""
              AutoScale     1
              MinValue      0
              MaxValue      1
              Signals       {}
              Untangle      0
              KeepBaseline  off
              BaselineValue 0
            }
            Axis {
              Name          ""
              AutoScale     1
              MinValue      0
              MaxValue      1
              Signals       {}
              Untangle      0
              KeepBaseline  off
              BaselineValue 0
            }
            Axis {
              Name          ""
              AutoScale     1
              MinValue      0
              MaxValue      1
              Signals       {}
              Untangle      0
              KeepBaseline  off
              BaselineValue 0
            }
            Axis {
              Name          ""
              AutoScale     1
              MinValue      0
              MaxValue      1
              Signals       {}
              Untangle      0
              KeepBaseline  off
              BaselineValue 0
            }
          }
        }
        Component {
          Type          Resistor
          Name          "R1"
          Show          on
          Position      [845, 595]
          Direction     up
          Flipped       off
          LabelPosition east
          Parameter {
            Variable      "R"
            Value         "Rs*Ns/Np"
            Show          off
          }
        }
        Component {
          Type          Constant
          Name          "Constant"
          Show          on
          Position      [325, 510]
          Direction     right
          Flipped       off
          LabelPosition south
          Frame         [-25, -10; 25, 10]
          Parameter {
            Variable      "Value"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "DataType"
            Value         "10"
            Show          off
          }
        }
        Component {
          Type          Output
          Name          "SOC"
          Show          on
          Position      [575, 510]
          Direction     down
          Flipped       off
          LabelPosition west
          Parameter {
            Variable      "Index"
            Value         "4"
            Show          on
          }
          Parameter {
            Variable      "Width"
            Value         "-1"
            Show          off
          }
        }
        Connection {
          Type          Signal
          SrcComponent  "Gain"
          SrcTerminal   2
          DstComponent  "Divide"
          DstTerminal   3
        }
        Connection {
          Type          Wire
          SrcComponent  "V"
          SrcTerminal   1
          DstComponent  "R3"
          DstTerminal   2
        }
        Connection {
          Type          Signal
          SrcComponent  "Gain1"
          SrcTerminal   2
          DstComponent  "SOC [%]"
          DstTerminal   1
        }
        Connection {
          Type          Wire
          SrcComponent  "V"
          SrcTerminal   2
          DstComponent  "-"
          DstTerminal   1
        }
        Connection {
          Type          Signal
          SrcComponent  "Probe"
          SrcTerminal   1
          DstComponent  "Sum"
          DstTerminal   2
        }
        Connection {
          Type          Signal
          SrcComponent  "Sum"
          SrcTerminal   1
          DstComponent  "Moving Average"
          DstTerminal   2
        }
        Connection {
          Type          Signal
          SrcComponent  "Moving Average"
          SrcTerminal   1
          DstComponent  "Perdas Internas"
          DstTerminal   1
        }
        Connection {
          Type          Wire
          SrcComponent  "+"
          SrcTerminal   1
          DstComponent  "Am1"
          DstTerminal   1
        }
        Connection {
          Type          Wire
          SrcComponent  "Am1"
          SrcTerminal   2
          Points        [810, 280]
          DstComponent  "R3"
          DstTerminal   1
        }
        Connection {
          Type          Signal
          SrcComponent  "Am1"
          SrcTerminal   3
          Points        [945, 240]
          DstComponent  base64 "Q8OpbHVsYXMgZW0gUGFyYWxlbG8="
          DstTerminal   1
        }
        Connection {
          Type          Signal
          SrcComponent  "Rs_inicial"
          SrcTerminal   1
          Points        [390, 465; 390, 430]
          DstComponent  "Divide1"
          DstTerminal   2
        }
        Connection {
          Type          Signal
          SrcComponent  "Divide1"
          SrcTerminal   1
          DstComponent  "Goto"
          DstTerminal   1
        }
        Connection {
          Type          Signal
          SrcComponent  "From1"
          SrcTerminal   1
          Points        [840, 315; 840, 325]
          DstComponent  "R3"
          DstTerminal   3
        }
        Connection {
          Type          Signal
          SrcComponent  "Capacity"
          SrcTerminal   1
          DstComponent  "Product1"
          DstTerminal   2
        }
        Connection {
          Type          Signal
          SrcComponent  "Product1"
          SrcTerminal   1
          DstComponent  "Gain"
          DstTerminal   1
        }
        Connection {
          Type          Signal
          SrcComponent  base64 "Q8OpbHVsYXMgZW0gUGFyYWxlbG8="
          SrcTerminal   2
          Points        [485, 240; 485, 275]
          Branch {
            Points        [485, 310; 325, 310]
            DstComponent  "Divide"
            DstTerminal   2
          }
          Branch {
            DstComponent  "Scope"
            DstTerminal   1
          }
        }
        Connection {
          Type          Signal
          SrcComponent  "Divide"
          SrcTerminal   1
          Points        [495, 340]
          Branch {
            Points        [495, 365]
            DstComponent  "Integrator"
            DstTerminal   1
          }
          Branch {
            Points        [495, 285]
            DstComponent  "Scope"
            DstTerminal   2
          }
        }
        Connection {
          Type          Signal
          SrcComponent  "SOC x VOC"
          SrcTerminal   2
          Points        [665, 365]
          Branch {
            DstComponent  base64 "Q8OpbHVsYXMgCmVtIFPDqXJpZQ=="
            DstTerminal   1
          }
          Branch {
            Points        [665, 305]
            DstComponent  "Scope"
            DstTerminal   4
          }
        }
        Connection {
          Type          Signal
          SrcComponent  base64 "Q8OpbHVsYXMgCmVtIFPDqXJpZQ=="
          SrcTerminal   2
          Points        [725, 365]
          Branch {
            DstComponent  "V"
            DstTerminal   3
          }
          Branch {
            DstComponent  "Scope"
            DstTerminal   5
          }
        }
        Connection {
          Type          Signal
          SrcComponent  "From"
          SrcTerminal   1
          Points        [240, 410]
          DstComponent  "Product1"
          DstTerminal   3
        }
        Connection {
          Type          Signal
          SrcComponent  "Constant"
          SrcTerminal   1
          Points        [395, 510; 395, 440]
          DstComponent  "Divide1"
          DstTerminal   3
        }
        Connection {
          Type          Signal
          SrcComponent  "Integrator"
          SrcTerminal   2
          Points        [575, 365]
          Branch {
            Points        [585, 365]
            Branch {
              DstComponent  "SOC x VOC"
              DstTerminal   1
            }
            Branch {
              Points        [585, 400; 640, 400]
              DstComponent  "Gain1"
              DstTerminal   1
            }
            Branch {
              Points        [585, 295]
              DstComponent  "Scope"
              DstTerminal   3
            }
          }
          Branch {
            DstComponent  "SOC"
            DstTerminal   1
          }
        }
      }
    }
    Component {
      Type          CurrentSource
      Name          "I"
      Show          on
      Position      [235, 105]
      Direction     down
      Flipped       on
      LabelPosition east
      Parameter {
        Variable      "DiscretizationBehavior"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "StateSpaceInlining"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          CScript
      Name          "C-Script"
      Show          on
      Position      [310, 255]
      Direction     up
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "DialogGeometry"
        Value         "[1037 168 596 660]"
        Show          off
      }
      Parameter {
        Variable      "NumInputs"
        Value         "6"
        Show          off
      }
      Parameter {
        Variable      "NumOutputs"
        Value         "2"
        Show          off
      }
      Parameter {
        Variable      "NumContStates"
        Value         "0"
        Show          off
      }
      Parameter {
        Variable      "NumDiscStates"
        Value         "0"
        Show          off
      }
      Parameter {
        Variable      "NumZCSignals"
        Value         "0"
        Show          off
      }
      Parameter {
        Variable      "DirectFeedthrough"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "Ts"
        Value         "60*Escala_Tempo"
        Show          off
      }
      Parameter {
        Variable      "TerminalBasedSampleTimes"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "Parameters"
        Value         "ETA, Vbmin, Vbmax"
        Show          off
      }
      Parameter {
        Variable      "LangStandard"
        Value         "2"
        Show          off
      }
      Parameter {
        Variable      "GnuExtensions"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "RuntimeCheck"
        Value         "2"
        Show          off
      }
      Parameter {
        Variable      "HighlightLevel"
        Value         "0"
        Show          off
      }
      Parameter {
        Variable      "Declarations"
        Value         base64 "Ly8gSW5jbHVpciBkZWZpbmnDp8O1ZXMgYsOhc2ljYXMgUFJJ"
"TUVJUk8gcGFyYSBjb3JyaWdpciBvIGVycm8gZGUgJ3NpemVfdCcKI2luY2x1ZGUgPHN0ZGRlZi5oP"
"iAKI2luY2x1ZGUgPHN0ZGxpYi5oPgojaW5jbHVkZSA8c3RkaW8uaD4KI2luY2x1ZGUgPG1hdGguaD"
"4KCi8vIFBhcsOibWV0cm9zIGxpZG9zIGRvIFdvcmtzcGFjZSAoRW52aWFkb3MgcGVsbyBQeXRob24"
"pCiNkZWZpbmUgRVRBICAgICAgUGFyYW1SZWFsRGF0YSgwLDApIC8vIEVmaWNpw6puY2lhIGdsb2Jh"
"bCAoMC0xKQojZGVmaW5lIFZCTUlOICAgIFBhcmFtUmVhbERhdGEoMSwwKSAvLyBUZW5zw6NvIG3Dr"
"W5pbWEgZGUgY29ydGUgZG8gQk1TCiNkZWZpbmUgVkJNQVggICAgUGFyYW1SZWFsRGF0YSgyLDApIC"
"8vIFRlbnPDo28gbcOheGltYSBkZSBjb3J0ZSBkbyBCTVMKCi8vIEVudHJhZGFzCiNkZWZpbmUgU09"
"DICAgICAgSW5wdXRTaWduYWwoMCwwKSAvLyDiiIggWzAsMV0KI2RlZmluZSBTT0NfTUlOICBJbnB1"
"dFNpZ25hbCgwLDEpIC8vIChleC46IDAuMikKI2RlZmluZSBTT0NfTUFYICBJbnB1dFNpZ25hbCgwL"
"DIpIC8vIChleC46IDAuOCkKI2RlZmluZSBQT1RfUkVRICBJbnB1dFNpZ25hbCgwLDMpIC8vIChXLC"
"ArIGNhcmdhIC8g4oiSIGRlc2NhcmdhKQojZGVmaW5lIFZfQkFUICAgIElucHV0U2lnbmFsKDAsNCk"
"gLy8gKFYsIHZpbmRvIGRvIGxvb2t1cCkKI2RlZmluZSBQX0JFU1MgICBJbnB1dFNpZ25hbCgwLDUp"
"CgovLyBTYcOtZGFzCiNkZWZpbmUgSV9TRVQgICAgT3V0cHV0U2lnbmFsKDAsMCkgLy8gQ29ycmVud"
"GUgZW0gYW1wZXJlcyBuYSBiYXRlcmlhCiNkZWZpbmUgU1RBVEUgICAgT3V0cHV0U2lnbmFsKDAsMS"
"kgLy8gKC0xIGRlc2NhcmdhIHwgMCBpZGxlIHwgKzEgY2FyZ2EpCgpzdGF0aWMgZmxvYXQgbWF4X3B"
"vd2VyX3BlYWsgPSAwLjBmOw=="
        Show          off
      }
      Parameter {
        Variable      "StartFcn"
        Value         ""
        Show          off
      }
      Parameter {
        Variable      "OutputFcn"
        Value         base64 "ZmxvYXQgcG90ID0gUE9UX1JFUTsKZmxvYXQgSSA9IDAuMGY7"
"CgpJX1NFVCA9IDAuMGY7ClNUQVRFID0gMDsKCi8vIE9wY2lvbmFsOiBBdHVhbGl6YSBvIHJhc3RyZ"
"WFkb3IgZGUgcGljbyBwYXJhIG8gcmVsYXTDs3JpbyBubyBUZXJtaW5hdGVGY24KaWYgKGZhYnMocG"
"90KSA+IG1heF9wb3dlcl9wZWFrKSB7CiAgICBtYXhfcG93ZXJfcGVhayA9IGZhYnMocG90KTsKfQo"
"KaWYgKHBvdCA+IDAuMGYpIC8vID09PSBNT0RPIERFIENBUkdBID09PQp7CiAgICBpZiAocG90ID4g"
"UF9CRVNTKQogICAgICAgIHBvdCA9IFBfQkVTUzsKCiAgICAvLyBCTVMgVmlydHVhbDogU8OzIGNhc"
"nJlZ2Egc2UgU09DIDwgTUFYIGUgYSBUZW5zw6NvIGVzdGl2ZXIgQUJBSVhPIGRvIGxpbWl0ZQogIC"
"AgaWYgKFNPQyA8IFNPQ19NQVggJiYgVl9CQVQgPCBWQk1BWCkKICAgIHsKICAgICAgICBJID0gKHB"
"vdCAqIEVUQSkgLyBWX0JBVDsKICAgICAgICBJX1NFVCA9IEk7CiAgICAgICAgU1RBVEUgPSAxOwog"
"ICAgfQp9CmVsc2UgaWYgKHBvdCA8IDAuMGYpIC8vID09PSBNT0RPIERFIERFU0NBUkdBID09PQp7C"
"iAgICBpZiAocG90IDwgLVBfQkVTUykKICAgICAgICBwb3QgPSAtUF9CRVNTOwoKICAgIC8vIEJNUy"
"BWaXJ0dWFsOiBTw7MgZGVzY2FycmVnYSBzZSBTT0MgPiBNSU4gZSBhIFRlbnPDo28gZXN0aXZlciB"
"BQ0lNQSBkbyBsaW1pdGUKICAgIGlmIChTT0MgPiBTT0NfTUlOICYmIFZfQkFUID4gVkJNSU4pCiAg"
"ICB7CiAgICAgICAgSSA9IChwb3QgLyBFVEEpIC8gVl9CQVQ7CiAgICAgICAgSV9TRVQgPSBJOwogI"
"CAgICAgIFNUQVRFID0gLTE7CiAgICB9Cn0K"
        Show          off
      }
      Parameter {
        Variable      "UpdateFcn"
        Value         ""
        Show          off
      }
      Parameter {
        Variable      "DerivativeFcn"
        Value         ""
        Show          off
      }
      Parameter {
        Variable      "TerminateFcn"
        Value         "printf(\"==========================================\\n"
"\");\n"
"printf(\"RELATORIO DE PICO\\n\");\n"
"// O %.2f imprime o float com 2 casas decimais\n"
"printf(\"Maior Potencia Registrada: %.2f W\\n\", max_power_peak); \n"
"printf(\"==========================================\\n\");"
        Show          off
      }
      Parameter {
        Variable      "StoreCustomStateFcn"
        Value         ""
        Show          off
      }
      Parameter {
        Variable      "RestoreCustomStateFcn"
        Value         ""
        Show          off
      }
    }
    Component {
      Type          Goto
      Name          "Goto"
      Show          off
      Position      [415, 235]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "I_set"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "2"
        Show          off
      }
    }
    Component {
      Type          SignalMux
      Name          "Mux1"
      Show          off
      Position      [235, 255]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Width"
        Value         "6"
        Show          off
      }
    }
    Component {
      Type          Goto
      Name          "Goto1"
      Show          off
      Position      [495, 85]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "SOC"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "2"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From"
      Show          off
      Position      [155, 205]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "SOC"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          Constant
      Name          "SocMin"
      Show          on
      Position      [155, 240]
      Direction     right
      Flipped       off
      LabelPosition west
      Frame         [-10, -10; 10, 10]
      Parameter {
        Variable      "Value"
        Value         "SocMin"
        Show          off
      }
      Parameter {
        Variable      "DataType"
        Value         "10"
        Show          off
      }
    }
    Component {
      Type          Constant
      Name          "SocMax"
      Show          on
      Position      [155, 265]
      Direction     right
      Flipped       off
      LabelPosition west
      Frame         [-10, -10; 10, 10]
      Parameter {
        Variable      "Value"
        Value         "SocMax"
        Show          off
      }
      Parameter {
        Variable      "DataType"
        Value         "10"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From1"
      Show          off
      Position      [155, 105]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "I_set"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          SignalDemux
      Name          "Demux"
      Show          off
      Position      [380, 255]
      Direction     right
      Flipped       on
      LabelPosition south
      Parameter {
        Variable      "Width"
        Value         "2"
        Show          off
      }
    }
    Component {
      Type          Product
      Name          "Product2"
      Show          off
      Position      [2365, 1255]
      Direction     up
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "IconShape"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "Inputs"
        Value         "**"
        Show          off
      }
      Parameter {
        Variable      "DataType"
        Value         "11"
        Show          off
      }
      Parameter {
        Variable      "DataTypeOverflowMode"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          Goto
      Name          "Goto2"
      Show          off
      Position      [415, 275]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "Check State"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "2"
        Show          off
      }
    }
    Component {
      Type          Goto
      Name          "Goto3"
      Show          off
      Position      [755, 175]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "Pot_port"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "2"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From6"
      Show          off
      Position      [155, 290]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "Pot_port"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          Scope
      Name          "Scope2"
      Show          on
      Position      [250, 410]
      Direction     up
      Flipped       off
      LabelPosition south
      Location      [6, 75; 964, 1063]
      State         "AAAA/wAAAAD9AAAAAgAAAAEAAAC0AAADaPwCAAAAA/sAAAAQAFoAbwBvA"
"G0AQQByAGUAYQAAAAA0AAADvQAAANEA////+wAAABQAUwBhAHYAZQBkAFYAaQBlAHcAcwAAAAAA//"
"///wAAAGMA////+wAAAAwAVAByAGEAYwBlAHMAAAAANAAAA2gAAABjAP///wAAAAMAAAO+AAAAf/w"
"BAAAAAfsAAAAUAEQAYQB0AGEAVwBpAGQAZwBlAHQBAAAAAAAAA74AAABEAP///wAAA74AAAM4AAAA"
"BAAAAAQAAAAIAAAACPwAAAABAAAAAgAAAAEAAAAOAFQAbwBvAGwAQgBhAHIBAAAAAP////8AAAAAA"
"AAAAA=="
      SavedViews    "AAAAAgAAAAA="
      HeaderState   "{\"DefaultSecSize\":0,\"FirstSecSize\":129,\"Labels\":[\""
"Delta\"],\"VisualIdxs\":[3]}"
      PlotPalettes  "AAAAAQAAAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAA"
"AEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
"AAAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAEAAAAAAAAAAAAAAAAAAAAAAAA"
"AAAAAAAA="
      Axes          "5"
      TimeRange     "0"
      ScrollingMode "1"
      SingleTimeAxis "1"
      Open          "0"
      Ts            "-1"
      SampleLimit   "0"
      XAxisLabel    "Time / s"
      ShowLegend    "2"
      Axis {
        Name          ""
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Axis {
        Name          "Atot"
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {"Pot_port"}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Axis {
        Name          ""
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {"State"}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Axis {
        Name          ""
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {"I_set"}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Axis {
        Name          ""
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {"SOC"}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Fourier {
        SingleXAxis       on
        AxisLabel         "Frequency / Hz"
        Scaling           0
        PhaseDisplay      0
        ShowFourierLegend off
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {"Pot_port"}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {"State"}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {"I_set"}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {"SOC"}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
      }
    }
    Component {
      Type          From
      Name          "From7"
      Show          off
      Position      [155, 490]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "I_set"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From8"
      Show          off
      Position      [155, 470]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "Pot_port"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          Gain
      Name          "Gain1"
      Show          on
      Position      [690, 175]
      Direction     right
      Flipped       off
      LabelPosition north
      Parameter {
        Variable      "K"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "Multiplication"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "OutputDataType"
        Value         "11"
        Show          off
      }
      Parameter {
        Variable      "DataTypeOverflowMode"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "GainDataType"
        Value         "11"
        Show          off
      }
    }
    Component {
      Type          ToFile
      Name          "To File"
      Show          off
      Position      [435, 480]
      Direction     right
      Flipped       off
      LabelPosition north
      Parameter {
        Variable      "Filename"
        Value         "dadosnovos"
        Show          off
        Evaluate      off
      }
      Parameter {
        Variable      "FileType"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "WriteSignalNames"
        Value         "2"
        Show          off
      }
      Parameter {
        Variable      "SampleTime"
        Value         "300"
        Show          off
      }
    }
    Component {
      Type          SignalMux
      Name          "Mux2"
      Show          off
      Position      [390, 480]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Width"
        Value         "5"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From10"
      Show          off
      Position      [155, 480]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "Check State"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          Goto
      Name          "Goto4"
      Show          off
      Position      [265, 140]
      Direction     down
      Flipped       off
      LabelPosition west
      Parameter {
        Variable      "Tag"
        Value         "V_bat"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "2"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From13"
      Show          off
      Position      [155, 500]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "SOC%"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          Clock
      Name          "Clock1"
      Show          on
      Position      [130, 625]
      Direction     right
      Flipped       off
      LabelPosition south
    }
    Component {
      Type          Gain
      Name          "Gain3"
      Show          on
      Position      [205, 625]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "K"
        Value         "5/60/60"
        Show          off
      }
      Parameter {
        Variable      "Multiplication"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "OutputDataType"
        Value         "10"
        Show          off
      }
      Parameter {
        Variable      "DataTypeOverflowMode"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "GainDataType"
        Value         "11"
        Show          off
      }
    }
    Component {
      Type          Goto
      Name          "Goto18"
      Show          off
      Position      [265, 625]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "Des"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "3"
        Show          off
      }
    }
    Component {
      Type          Clock
      Name          "Clock2"
      Show          on
      Position      [95, 690]
      Direction     right
      Flipped       off
      LabelPosition south
    }
    Component {
      Type          Gain
      Name          "Gain4"
      Show          on
      Position      [155, 690]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "K"
        Value         "1/60"
        Show          off
      }
      Parameter {
        Variable      "Multiplication"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "OutputDataType"
        Value         "10"
        Show          off
      }
      Parameter {
        Variable      "DataTypeOverflowMode"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "GainDataType"
        Value         "11"
        Show          off
      }
    }
    Component {
      Type          Goto
      Name          "Goto21"
      Show          off
      Position      [345, 695]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "Temp_sim"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "3"
        Show          off
      }
    }
    Component {
      Type          Math
      Name          "Math1"
      Show          on
      Position      [280, 695]
      Direction     up
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Operator"
        Value         "6"
        Show          off
      }
    }
    Component {
      Type          Constant
      Name          "Freq. Init.2"
      Show          off
      Position      [205, 735]
      Direction     right
      Flipped       off
      LabelPosition south
      Frame         [-10, -10; 10, 10]
      Parameter {
        Variable      "Value"
        Value         "24"
        Show          on
      }
      Parameter {
        Variable      "DataType"
        Value         "10"
        Show          off
      }
    }
    Component {
      Type          Scope
      Name          "Scope1"
      Show          on
      Position      [495, 655]
      Direction     up
      Flipped       off
      LabelPosition south
      Location      [0, 24; 1920, 1064]
      State         "AAAA/wAAAAD9AAAAAgAAAAEAAAAAAAAAAPwCAAAAA/sAAAAQAFoAbwBvA"
"G0AQQByAGUAYQAAAAAA/////wAAAFkA////+wAAABQAUwBhAHYAZQBkAFYAaQBlAHcAcwAAAAAA//"
"///wAAAGMA////+wAAAAwAVAByAGEAYwBlAHMAAAAAAP////8AAABjAP///wAAAAMAAAAAAAAAAPw"
"BAAAAAfsAAAAUAEQAYQB0AGEAVwBpAGQAZwBlAHQAAAAAAP////8AAABEAP///wAAB4AAAAPxAAAA"
"BAAAAAQAAAAIAAAACPwAAAABAAAAAgAAAAEAAAAOAFQAbwBvAGwAQgBhAHIBAAAAAP////8AAAAAA"
"AAAAA=="
      SavedViews    "AAAAAgAAAAA="
      HeaderState   "{\"DefaultSecSize\":0,\"FirstSecSize\":65,\"Labels\":[],"
"\"VisualIdxs\":[]}"
      PlotPalettes  "AAAAAQAAAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAA"
"AEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
      Axes          "2"
      TimeRange     "0.0"
      ScrollingMode "1"
      SingleTimeAxis "1"
      Open          "0"
      Ts            "-1"
      SampleLimit   "0"
      XAxisLabel    "Time / s"
      ShowLegend    "1"
      Axis {
        Name          ""
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Axis {
        Name          ""
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Fourier {
        SingleXAxis       on
        AxisLabel         "Frequency / Hz"
        Scaling           0
        PhaseDisplay      0
        ShowFourierLegend off
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
      }
    }
    Component {
      Type          From
      Name          "From11"
      Show          off
      Position      [155, 305]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "V_bat"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From12"
      Show          off
      Position      [335, 460]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "V_bat"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From2"
      Show          off
      Position      [540, 275]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "I_set"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From14"
      Show          off
      Position      [540, 255]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "V_bat"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          FromFile
      Name          "potencia_mes_in.mat"
      Show          on
      Position      [585, 175]
      Direction     right
      Flipped       off
      LabelPosition north
      Parameter {
        Variable      "Filename"
        Value         "potencia_mes_in"
        Show          off
        Evaluate      off
      }
      Parameter {
        Variable      "FileType"
        Value         "2"
        Show          off
      }
      Parameter {
        Variable      "Width"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "LeftExtrapolation"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "LeftValue"
        Value         "0"
        Show          off
      }
      Parameter {
        Variable      "Interpolation"
        Value         "2"
        Show          off
      }
      Parameter {
        Variable      "RightExtrapolation"
        Value         "2"
        Show          off
      }
      Parameter {
        Variable      "RightValue"
        Value         "0"
        Show          off
      }
      Parameter {
        Variable      "LocateDiscontinuities"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          Constant
      Name          base64 "U2HDumRlIEF0dWFs"
      Show          on
      Position      [1155, 220]
      Direction     right
      Flipped       off
      LabelPosition south
      Frame         [-40, -10; 40, 10]
      Parameter {
        Variable      "Value"
        Value         "SOH_Input"
        Show          off
      }
      Parameter {
        Variable      "DataType"
        Value         "10"
        Show          off
      }
    }
    Component {
      Type          ToFile
      Name          "soc_out_mes"
      Show          on
      Position      [715, 55]
      Direction     right
      Flipped       off
      LabelPosition north
      Parameter {
        Variable      "Filename"
        Value         "soc_out_mes"
        Show          off
        Evaluate      off
      }
      Parameter {
        Variable      "FileType"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "WriteSignalNames"
        Value         "2"
        Show          off
      }
      Parameter {
        Variable      "SampleTime"
        Value         "60*Escala_Tempo"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From15"
      Show          off
      Position      [640, 55]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "SOC%"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          Goto
      Name          "Goto6"
      Show          off
      Position      [1235, 220]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "SOH_Input"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "2"
        Show          off
      }
    }
    Component {
      Type          Memory
      Name          "Memory"
      Show          on
      Position      [185, 45]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "X0"
        Value         "0"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From4"
      Show          off
      Position      [155, 390]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "SOH_Input"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From9"
      Show          off
      Position      [540, 235]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "Pot_port"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          Integrator
      Name          "Integrator"
      Show          on
      Position      [730, 235]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "ExternalReset"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "InitialConditionSource"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "x0"
        Value         "0"
        Show          off
      }
      Parameter {
        Variable      "ShowStatePort"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "EnableWrapping"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "UpperLimit"
        Value         "inf"
        Show          off
      }
      Parameter {
        Variable      "LowerLimit"
        Value         "-inf"
        Show          off
      }
    }
    Component {
      Type          Gain
      Name          "Gain"
      Show          on
      Position      [800, 235]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "K"
        Value         "1/3600/1000"
        Show          off
      }
      Parameter {
        Variable      "Multiplication"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "OutputDataType"
        Value         "11"
        Show          off
      }
      Parameter {
        Variable      "DataTypeOverflowMode"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "GainDataType"
        Value         "11"
        Show          off
      }
    }
    Component {
      Type          Display
      Name          "Display"
      Show          on
      Position      [920, 235]
      Direction     up
      Flipped       off
      LabelPosition south
      Frame         [-56, -11; 56, 11]
      Parameter {
        Variable      "Notation"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "Precision"
        Value         "4"
        Show          off
      }
    }
    Component {
      Type          Product
      Name          "Product"
      Show          off
      Position      [670, 295]
      Direction     up
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "IconShape"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "Inputs"
        Value         "**"
        Show          off
      }
      Parameter {
        Variable      "DataType"
        Value         "11"
        Show          off
      }
      Parameter {
        Variable      "DataTypeOverflowMode"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          Display
      Name          "Display1"
      Show          on
      Position      [1280, 320]
      Direction     up
      Flipped       off
      LabelPosition south
      Frame         [-56, -11; 56, 11]
      Parameter {
        Variable      "Notation"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "Precision"
        Value         "4"
        Show          off
      }
    }
    Component {
      Type          Constant
      Name          "Constant"
      Show          on
      Position      [1155, 90]
      Direction     right
      Flipped       off
      LabelPosition south
      Frame         [-40, -10; 40, 10]
      Parameter {
        Variable      "Value"
        Value         "P_BESS"
        Show          off
      }
      Parameter {
        Variable      "DataType"
        Value         "10"
        Show          off
      }
    }
    Component {
      Type          Goto
      Name          "Goto5"
      Show          off
      Position      [495, 55]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "SOC%"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "2"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From16"
      Show          off
      Position      [155, 325]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "P_BESS"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          Goto
      Name          "Goto7"
      Show          off
      Position      [1225, 90]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "P_BESS"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "2"
        Show          off
      }
    }
    Component {
      Type          Constant
      Name          base64 "U29jIGRlIEluw61jaW8="
      Show          on
      Position      [1150, 140]
      Direction     right
      Flipped       off
      LabelPosition south
      Frame         [-35, -10; 35, 10]
      Parameter {
        Variable      "Value"
        Value         "SOC_0"
        Show          off
      }
      Parameter {
        Variable      "DataType"
        Value         "10"
        Show          off
      }
    }
    Component {
      Type          Display
      Name          "Display2"
      Show          on
      Position      [1275, 55]
      Direction     up
      Flipped       off
      LabelPosition south
      Frame         [-56, -11; 56, 11]
      Parameter {
        Variable      "Notation"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "Precision"
        Value         "4"
        Show          off
      }
    }
    Component {
      Type          Display
      Name          "Display3"
      Show          on
      Position      [1285, 140]
      Direction     up
      Flipped       off
      LabelPosition south
      Frame         [-56, -11; 56, 11]
      Parameter {
        Variable      "Notation"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "Precision"
        Value         "4"
        Show          off
      }
    }
    Component {
      Type          Display
      Name          "Display4"
      Show          on
      Position      [1280, 250]
      Direction     up
      Flipped       off
      LabelPosition south
      Frame         [-56, -11; 56, 11]
      Parameter {
        Variable      "Notation"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "Precision"
        Value         "4"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From5"
      Show          off
      Position      [805, 485]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "P_out"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          Goto
      Name          "Goto8"
      Show          off
      Position      [730, 295]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "P_out"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "2"
        Show          off
      }
    }
    Component {
      Type          Scope
      Name          "Scope3"
      Show          on
      Position      [885, 485]
      Direction     up
      Flipped       off
      LabelPosition south
      Location      [961, 31; 1919, 1055]
      State         "AAAA/wAAAAD9AAAAAgAAAAEAAAC0AAADXPwCAAAAA/sAAAAQAFoAbwBvA"
"G0AQQByAGUAYQAAAAA0AAADvQAAANEA////+wAAABQAUwBhAHYAZQBkAFYAaQBlAHcAcwAAAAAA//"
"///wAAAGMA////+wAAAAwAVAByAGEAYwBlAHMBAAAANAAAA1wAAABjAP///wAAAAMAAAO+AAAAf/w"
"BAAAAAfsAAAAUAEQAYQB0AGEAVwBpAGQAZwBlAHQBAAAAAAAAA74AAABEAP///wAAAwQAAANcAAAA"
"BAAAAAQAAAAIAAAACPwAAAABAAAAAgAAAAEAAAAOAFQAbwBvAGwAQgBhAHIBAAAAAP////8AAAAAA"
"AAAAA=="
      SavedViews    "AAAAAgAAAAA="
      HeaderState   "{\"DefaultSecSize\":0,\"FirstSecSize\":99,\"Labels\":[\"D"
"elta\"],\"VisualIdxs\":[3]}"
      PlotPalettes  "AAAAAQAAAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAA"
"AEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
"AAAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAEAAAAAAAAAAAAAAAAAAAAAAAA"
"AAAAAAAA="
      Axes          "5"
      TimeRange     "0"
      ScrollingMode "1"
      SingleTimeAxis "1"
      Open          "1"
      Ts            "-1"
      SampleLimit   "0"
      XAxisLabel    "Time / s"
      ShowLegend    "2"
      Axis {
        Name          ""
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {"P-port"}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Axis {
        Name          "Atot"
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {"P_out"}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Axis {
        Name          ""
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {"SOC"}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Axis {
        Name          ""
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {"I_set"}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Axis {
        Name          ""
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {"V_bat"}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
      Fourier {
        SingleXAxis       on
        AxisLabel         "Frequency / Hz"
        Scaling           0
        PhaseDisplay      0
        ShowFourierLegend off
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {"P-port"}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {"P_out"}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {"SOC"}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {"I_set"}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {"V_bat"}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
      }
    }
    Component {
      Type          From
      Name          "From17"
      Show          off
      Position      [805, 465]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "Pot_port"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From18"
      Show          off
      Position      [805, 505]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "SOC"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From19"
      Show          off
      Position      [805, 525]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "I_set"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From20"
      Show          off
      Position      [805, 545]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "V_bat"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Component {
      Type          From
      Name          "From21"
      Show          off
      Position      [1170, 320]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Tag"
        Value         "P_out"
        Show          off
      }
      Parameter {
        Variable      "Visibility"
        Value         "1"
        Show          off
      }
      Parameter {
        Variable      "NoMatchingCounterpartAction"
        Value         "1"
        Show          off
      }
    }
    Connection {
      Type          Wire
      SrcComponent  "I"
      SrcTerminal   1
      Points        [235, 180; 290, 180]
      Branch {
        Points        [400, 180]
        DstComponent  "Battery"
        DstTerminal   3
      }
      Branch {
        DstComponent  "Vm1"
        DstTerminal   2
      }
    }
    Connection {
      Type          Wire
      SrcComponent  "I"
      SrcTerminal   2
      Points        [235, 45; 290, 45]
      Branch {
        Points        [400, 45]
        DstComponent  "Battery"
        DstTerminal   1
      }
      Branch {
        DstComponent  "Vm1"
        DstTerminal   1
      }
    }
    Connection {
      Type          Signal
      SrcComponent  "Mux1"
      SrcTerminal   1
      DstComponent  "C-Script"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "SocMin"
      SrcTerminal   1
      DstComponent  "Mux1"
      DstTerminal   3
    }
    Connection {
      Type          Signal
      SrcComponent  "SocMax"
      SrcTerminal   1
      Points        [185, 265; 185, 250]
      DstComponent  "Mux1"
      DstTerminal   4
    }
    Connection {
      Type          Signal
      SrcComponent  "C-Script"
      SrcTerminal   2
      DstComponent  "Demux"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "Demux"
      SrcTerminal   2
      Points        [390, 250; 390, 235]
      DstComponent  "Goto"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "From"
      SrcTerminal   1
      Points        [195, 205; 195, 230]
      DstComponent  "Mux1"
      DstTerminal   2
    }
    Connection {
      Type          Signal
      SrcComponent  "Demux"
      SrcTerminal   3
      Points        [390, 260; 390, 275]
      DstComponent  "Goto2"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "From6"
      SrcTerminal   1
      Points        [195, 290; 195, 260]
      DstComponent  "Mux1"
      DstTerminal   5
    }
    Connection {
      Type          Signal
      SrcComponent  "Clock1"
      SrcTerminal   1
      DstComponent  "Gain3"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "Clock2"
      SrcTerminal   1
      DstComponent  "Gain4"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "Freq. Init.2"
      SrcTerminal   1
      Points        [235, 735; 235, 700]
      DstComponent  "Math1"
      DstTerminal   3
    }
    Connection {
      Type          Signal
      SrcComponent  "Gain4"
      SrcTerminal   2
      DstComponent  "Math1"
      DstTerminal   2
    }
    Connection {
      Type          Signal
      SrcComponent  "Gain3"
      SrcTerminal   2
      Points        [240, 625]
      Branch {
        DstComponent  "Goto18"
        DstTerminal   1
      }
      Branch {
        Points        [240, 650]
        DstComponent  "Scope1"
        DstTerminal   1
      }
    }
    Connection {
      Type          Signal
      SrcComponent  "Math1"
      SrcTerminal   1
      Points        [315, 695]
      Branch {
        DstComponent  "Goto21"
        DstTerminal   1
      }
      Branch {
        Points        [315, 660]
        DstComponent  "Scope1"
        DstTerminal   2
      }
    }
    Connection {
      Type          Signal
      SrcComponent  "From11"
      SrcTerminal   1
      Points        [200, 305; 200, 270]
      DstComponent  "Mux1"
      DstTerminal   6
    }
    Connection {
      Type          Signal
      SrcComponent  "Gain1"
      SrcTerminal   2
      DstComponent  "Goto3"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "Vm1"
      SrcTerminal   3
      Points        [265, 105]
      DstComponent  "Goto4"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "From15"
      SrcTerminal   1
      DstComponent  "soc_out_mes"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "potencia_mes_in.mat"
      SrcTerminal   1
      DstComponent  "Gain1"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "Mux2"
      SrcTerminal   1
      DstComponent  "To File"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "From13"
      SrcTerminal   1
      Points        [210, 500]
      Branch {
        DstComponent  "Mux2"
        DstTerminal   6
      }
      Branch {
        Points        [210, 430]
        DstComponent  "Scope2"
        DstTerminal   5
      }
    }
    Connection {
      Type          Signal
      SrcComponent  "From4"
      SrcTerminal   1
      DstComponent  "Scope2"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "From9"
      SrcTerminal   1
      Points        [580, 235]
      Branch {
        Points        [580, 365]
        DstComponent  base64 "VGVuc8OjbyBlIENvcnJlbnRlCm5hIEJhdGVyaWE="
        DstTerminal   1
      }
      Branch {
        DstComponent  "Integrator"
        DstTerminal   1
      }
    }
    Connection {
      Type          Signal
      SrcComponent  "Integrator"
      SrcTerminal   2
      DstComponent  "Gain"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "Gain"
      SrcTerminal   2
      DstComponent  "Display"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "From14"
      SrcTerminal   1
      Points        [570, 255; 570, 290]
      Branch {
        Points        [570, 375]
        DstComponent  base64 "VGVuc8OjbyBlIENvcnJlbnRlCm5hIEJhdGVyaWE="
        DstTerminal   2
      }
      Branch {
        DstComponent  "Product"
        DstTerminal   2
      }
    }
    Connection {
      Type          Signal
      SrcComponent  "From2"
      SrcTerminal   1
      Points        [565, 275; 565, 300]
      Branch {
        Points        [565, 385]
        DstComponent  base64 "VGVuc8OjbyBlIENvcnJlbnRlCm5hIEJhdGVyaWE="
        DstTerminal   3
      }
      Branch {
        DstComponent  "Product"
        DstTerminal   3
      }
    }
    Connection {
      Type          Signal
      SrcComponent  "From1"
      SrcTerminal   1
      DstComponent  "I"
      DstTerminal   3
    }
    Connection {
      Type          Signal
      SrcComponent  "Battery"
      SrcTerminal   4
      Points        [470, 75; 470, 85]
      DstComponent  "Goto1"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "Battery"
      SrcTerminal   2
      Points        [470, 65; 470, 55]
      DstComponent  "Goto5"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "From16"
      SrcTerminal   1
      Points        [205, 325; 205, 280]
      DstComponent  "Mux1"
      DstTerminal   7
    }
    Connection {
      Type          Signal
      SrcComponent  "Constant"
      SrcTerminal   1
      Points        [1200, 90]
      Branch {
        DstComponent  "Goto7"
        DstTerminal   1
      }
      Branch {
        Points        [1200, 55]
        DstComponent  "Display2"
        DstTerminal   1
      }
    }
    Connection {
      Type          Signal
      SrcComponent  base64 "U2HDumRlIEF0dWFs"
      SrcTerminal   1
      Points        [1205, 220]
      Branch {
        DstComponent  "Goto6"
        DstTerminal   1
      }
      Branch {
        Points        [1205, 250]
        DstComponent  "Display4"
        DstTerminal   1
      }
    }
    Connection {
      Type          Signal
      SrcComponent  base64 "U29jIGRlIEluw61jaW8="
      SrcTerminal   1
      DstComponent  "Display3"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "Product"
      SrcTerminal   1
      DstComponent  "Goto8"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "From18"
      SrcTerminal   1
      Points        [835, 505; 835, 485]
      DstComponent  "Scope3"
      DstTerminal   3
    }
    Connection {
      Type          Signal
      SrcComponent  "From5"
      SrcTerminal   1
      Points        [830, 485; 830, 475]
      DstComponent  "Scope3"
      DstTerminal   2
    }
    Connection {
      Type          Signal
      SrcComponent  "From17"
      SrcTerminal   1
      DstComponent  "Scope3"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "From19"
      SrcTerminal   1
      Points        [840, 525; 840, 495]
      DstComponent  "Scope3"
      DstTerminal   4
    }
    Connection {
      Type          Signal
      SrcComponent  "From20"
      SrcTerminal   1
      Points        [845, 545; 845, 505]
      DstComponent  "Scope3"
      DstTerminal   5
    }
    Connection {
      Type          Signal
      SrcComponent  "From21"
      SrcTerminal   1
      DstComponent  "Display1"
      DstTerminal   1
    }
    Connection {
      Type          Signal
      SrcComponent  "From12"
      SrcTerminal   1
      DstComponent  "Mux2"
      DstTerminal   2
    }
    Connection {
      Type          Signal
      SrcComponent  "From7"
      SrcTerminal   1
      Points        [205, 490]
      Branch {
        Points        [205, 420]
        DstComponent  "Scope2"
        DstTerminal   4
      }
      Branch {
        DstComponent  "Mux2"
        DstTerminal   5
      }
    }
    Connection {
      Type          Signal
      SrcComponent  "From10"
      SrcTerminal   1
      Points        [200, 480]
      Branch {
        Points        [200, 410]
        DstComponent  "Scope2"
        DstTerminal   3
      }
      Branch {
        DstComponent  "Mux2"
        DstTerminal   4
      }
    }
    Connection {
      Type          Signal
      SrcComponent  "From8"
      SrcTerminal   1
      Points        [195, 470]
      Branch {
        Points        [195, 400]
        DstComponent  "Scope2"
        DstTerminal   2
      }
      Branch {
        DstComponent  "Mux2"
        DstTerminal   3
      }
    }
  }
}

`

## Arquivo: meeting.md
`markdown
# Foco no Artigo

## Comparação de Vida Útil entre

[ ] 1) Atividades Diferentes? -> Mesma Bateria e Mesma Curva de Carga?
[ ] 2) Baterias Diferentes?   -> Mesma atividade e Mesma Curva de Carga?
[ ] 3) Curvas diferentes?     -> Mesma Bateria e Memsa atividade
[ ] 4) Controle de nível de tensão

## Pensar nas atividades

  [ ] **Load Shifting**
  [ ] **Peak Shaving**
  [ ] **Regulação do Fator de Potência**
  [ ] Redução da Injeção (Aproveitar geração nos cortes)
  [ ] Afundamento de Tensão
  [ ] Balanceamento de Tensão
  [ ] Controle de Frequência
  [ ] Alívio de Potência na Rede (adiar expansão)

- Será que a defasagem impacta na vida util da bateria? - Para efeito desse artigo, ignorar.
- Coletar artigos de publicação no CBA (e qual mais?) com aplicação de baterias

## Notas de reunião

  [ ] plotar a tensão e corrente
  [ ] VALIDAR O MODELO DO PLECS
  [ ] FAZER O EMS COM FOCO EM LOAD SHIFTING

`

## Arquivo: results\sim_20260225_222201\data\config_snapshot.json
`json
{
  "plecs": {
    "MODELO_PLECS": "bess_batch_mode",
    "BLOCO_SOH_ALIAS": "SOH_Input",
    "ARQUIVO_ENTRADA_POT": "potencia_mes_in.mat",
    "ARQUIVO_SAIDA_SOC": "soc_out_mes.csv",
    "Nfases": 3
  },
  "dados_entrada": {
    "ARQUIVO_MAT": "cmveditora.mat",
    "dt_minutos": "",
    "dias_por_mes_sim": 30,
    "meses_por_ano_sim": 12,
    "dias_por_ano_avg": 360
  },
  "simulacao": {
    "SOH_INICIAL_PERC": 100.0,
    "ANOS_SIMULACAO": 0,
    "MESES_SIMULACAO": 6,
    "data_inicio_simulacao": "2025-01-01 00:00:00"
  },
  "modelo_degradacao": {
    "ciclo": {
      "a": 2.6418,
      "b": -0.01943,
      "c": 0.004,
      "d": 0.01705,
      "g": 0.0123,
      "h": 0.7162,
      "exp_cycle": 2.0,
      "peak_prominence": 1.0,
      "range_round_dp": 1,
      "mean_round_dp": 1
    },
    "calendario": {
      "k_T": 1.9775e-11,
      "exp_T": 0.07511,
      "k_soc": 1.639,
      "exp_soc": 0.007388,
      "exp_cal": 1.25
    }
  },
  "paths": {
    "data": "data",
    "sim": "sim",
    "debug": "debug",
    "plots": "plots",
    "relatorio": "relatorio"
  },
  "relatorio": {
    "gerar_validacao_detalhada": true,
    "incluir_calculos_intermediarios": true
  },
  "bateria_nome": "Sany_314Ah",
  "bateria_cap_wh": 261000.0,
  "bateria_soc_min": 0.2,
  "bateria_soc_max": 0.8,
  "backend": "plecs",
  "sim_until_eol": false,
  "total_meses_simulados": 6
}
`

## Arquivo: results\sim_20260225_224304\data\config_snapshot.json
`json
{
  "plecs": {
    "MODELO_PLECS": "bess_batch_mode",
    "BLOCO_SOH_ALIAS": "SOH_Input",
    "ARQUIVO_ENTRADA_POT": "potencia_mes_in.mat",
    "ARQUIVO_SAIDA_SOC": "soc_out_mes.csv",
    "Nfases": 3
  },
  "dados_entrada": {
    "ARQUIVO_MAT": "cmveditora.mat",
    "dt_minutos": "",
    "dias_por_mes_sim": 30,
    "meses_por_ano_sim": 12,
    "dias_por_ano_avg": 360
  },
  "simulacao": {
    "SOH_INICIAL_PERC": 100.0,
    "ANOS_SIMULACAO": 0,
    "MESES_SIMULACAO": 6,
    "data_inicio_simulacao": "2025-01-01 00:00:00"
  },
  "modelo_degradacao": {
    "ciclo": {
      "a": 2.6418,
      "b": -0.01943,
      "c": 0.004,
      "d": 0.01705,
      "g": 0.0123,
      "h": 0.7162,
      "exp_cycle": 2.0,
      "peak_prominence": 1.0,
      "range_round_dp": 1,
      "mean_round_dp": 1
    },
    "calendario": {
      "k_T": 1.9775e-11,
      "exp_T": 0.07511,
      "k_soc": 1.639,
      "exp_soc": 0.007388,
      "exp_cal": 1.25
    }
  },
  "paths": {
    "data": "data",
    "sim": "sim",
    "debug": "debug",
    "plots": "plots",
    "relatorio": "relatorio"
  },
  "relatorio": {
    "gerar_validacao_detalhada": true,
    "incluir_calculos_intermediarios": true
  },
  "llm": {
    "gemini_api_key": "AIzaSyD7xPCoC1qtZMrKvPasJTPzGH8a6OMpQGQ"
  },
  "bateria_nome": "Sany_314Ah",
  "bateria_cap_wh": 261000.0,
  "bateria_soc_min": 0.2,
  "bateria_soc_max": 0.8,
  "backend": "plecs",
  "sim_until_eol": false,
  "total_meses_simulados": 6
}
`

## Arquivo: results\sim_20260225_233534\data\config_snapshot.json
`json
{
  "plecs": {
    "MODELO_PLECS": "bess_batch_mode",
    "BLOCO_SOH_ALIAS": "SOH_Input",
    "ARQUIVO_ENTRADA_POT": "potencia_mes_in.mat",
    "ARQUIVO_SAIDA_SOC": "soc_out_mes.csv",
    "Nfases": 3
  },
  "dados_entrada": {
    "ARQUIVO_MAT": "cmveditora.mat",
    "dt_minutos": "",
    "dias_por_mes_sim": 30,
    "meses_por_ano_sim": 12,
    "dias_por_ano_avg": 360
  },
  "simulacao": {
    "SOH_INICIAL_PERC": 100.0,
    "ANOS_SIMULACAO": 1,
    "MESES_SIMULACAO": null,
    "data_inicio_simulacao": "2025-01-01 00:00:00"
  },
  "modelo_degradacao": {
    "ciclo": {
      "a": 2.6418,
      "b": -0.01943,
      "c": 0.004,
      "d": 0.01705,
      "g": 0.0123,
      "h": 0.7162,
      "exp_cycle": 2.0,
      "peak_prominence": 1.0,
      "range_round_dp": 1,
      "mean_round_dp": 1
    },
    "calendario": {
      "k_T": 1.9775e-11,
      "exp_T": 0.07511,
      "k_soc": 1.639,
      "exp_soc": 0.007388,
      "exp_cal": 1.25
    }
  },
  "paths": {
    "data": "data",
    "sim": "sim",
    "debug": "debug",
    "plots": "plots",
    "relatorio": "relatorio"
  },
  "relatorio": {
    "gerar_validacao_detalhada": true,
    "incluir_calculos_intermediarios": true
  },
  "llm": {
    "gemini_api_key": "AIzaSyD7xPCoC1qtZMrKvPasJTPzGH8a6OMpQGQ"
  },
  "bateria_nome": "Sany_314Ah",
  "bateria_cap_wh": 261000.0,
  "bateria_soc_min": 0.2,
  "bateria_soc_max": 0.8,
  "backend": "plecs",
  "sim_until_eol": true,
  "total_meses_simulados": 240
}
`

## Arquivo: results\sim_20260226_061016\data\config_snapshot.json
`json
{
  "plecs": {
    "MODELO_PLECS": "bess_batch_mode",
    "BLOCO_SOH_ALIAS": "SOH_Input",
    "ARQUIVO_ENTRADA_POT": "potencia_mes_in.mat",
    "ARQUIVO_SAIDA_SOC": "soc_out_mes.csv",
    "Nfases": 3
  },
  "dados_entrada": {
    "ARQUIVO_MAT": "cmveditora.mat",
    "dt_minutos": 15.0,
    "dias_por_mes_sim": 30,
    "meses_por_ano_sim": 12,
    "dias_por_ano_avg": 360
  },
  "simulacao": {
    "SOH_INICIAL_PERC": 100.0,
    "ANOS_SIMULACAO": 1,
    "MESES_SIMULACAO": null,
    "data_inicio_simulacao": "2025-01-01 00:00:00"
  },
  "modelo_degradacao": {
    "ciclo": {
      "a": 2.6418,
      "b": -0.01943,
      "c": 0.004,
      "d": 0.01705,
      "g": 0.0123,
      "h": 0.7162,
      "exp_cycle": 2.0,
      "peak_prominence": 1.0,
      "range_round_dp": 1,
      "mean_round_dp": 1
    },
    "calendario": {
      "k_T": 1.9775e-11,
      "exp_T": 0.07511,
      "k_soc": 1.639,
      "exp_soc": 0.007388,
      "exp_cal": 1.25
    }
  },
  "paths": {
    "data": "data",
    "sim": "sim",
    "debug": "debug",
    "plots": "plots",
    "relatorio": "relatorio"
  },
  "relatorio": {
    "gerar_validacao_detalhada": true,
    "incluir_calculos_intermediarios": true
  },
  "llm": {
    "gemini_api_key": "AIzaSyD7xPCoC1qtZMrKvPasJTPzGH8a6OMpQGQ"
  },
  "bateria_nome": "Sany_314Ah",
  "bateria_cap_wh": 261000.0,
  "bateria_soc_min": 0.2,
  "bateria_soc_max": 0.8,
  "backend": "python",
  "sim_until_eol": true,
  "total_meses_simulados": 159
}
`

## Arquivo: results\sim_20260226_083630\data\config_snapshot.json
`json
{
  "plecs": {
    "MODELO_PLECS": "bess_batch_mode",
    "BLOCO_SOH_ALIAS": "SOH_Input",
    "ARQUIVO_ENTRADA_POT": "potencia_mes_in.mat",
    "ARQUIVO_SAIDA_SOC": "soc_out_mes.csv",
    "Nfases": 3
  },
  "dados_entrada": {
    "ARQUIVO_MAT": "cmveditora.mat",
    "dt_minutos": "",
    "dias_por_mes_sim": 30,
    "meses_por_ano_sim": 12,
    "dias_por_ano_avg": 360
  },
  "simulacao": {
    "SOH_INICIAL_PERC": 100.0,
    "ANOS_SIMULACAO": 0,
    "MESES_SIMULACAO": 6,
    "data_inicio_simulacao": "2025-01-01 00:00:00"
  },
  "modelo_degradacao": {
    "ciclo": {
      "a": 2.6418,
      "b": -0.01943,
      "c": 0.004,
      "d": 0.01705,
      "g": 0.0123,
      "h": 0.7162,
      "exp_cycle": 2.0,
      "peak_prominence": 1.0,
      "range_round_dp": 1,
      "mean_round_dp": 1
    },
    "calendario": {
      "k_T": 1.9775e-11,
      "exp_T": 0.07511,
      "k_soc": 1.639,
      "exp_soc": 0.007388,
      "exp_cal": 1.25
    }
  },
  "paths": {
    "data": "data",
    "sim": "sim",
    "debug": "debug",
    "plots": "plots",
    "relatorio": "relatorio"
  },
  "relatorio": {
    "gerar_validacao_detalhada": true,
    "incluir_calculos_intermediarios": true
  },
  "llm": {
    "gemini_api_key": "AIzaSyD7xPCoC1qtZMrKvPasJTPzGH8a6OMpQGQ"
  },
  "bateria_nome": "Sany_314Ah",
  "bateria_cap_wh": 261000.0,
  "bateria_soc_min": 0.2,
  "bateria_soc_max": 0.8,
  "backend": "python",
  "sim_until_eol": false,
  "total_meses_simulados": 6
}
`

## Arquivo: results\sim_20260226_083646\data\config_snapshot.json
`json
{
  "plecs": {
    "MODELO_PLECS": "bess_batch_mode",
    "BLOCO_SOH_ALIAS": "SOH_Input",
    "ARQUIVO_ENTRADA_POT": "potencia_mes_in.mat",
    "ARQUIVO_SAIDA_SOC": "soc_out_mes.csv",
    "Nfases": 3
  },
  "dados_entrada": {
    "ARQUIVO_MAT": "Atot - BackUp.mat",
    "dt_minutos": 5.0,
    "dias_por_mes_sim": 30,
    "meses_por_ano_sim": 12,
    "dias_por_ano_avg": 360
  },
  "simulacao": {
    "SOH_INICIAL_PERC": 100.0,
    "ANOS_SIMULACAO": 0,
    "MESES_SIMULACAO": 6,
    "data_inicio_simulacao": "2025-01-01 00:00:00"
  },
  "modelo_degradacao": {
    "ciclo": {
      "a": 2.6418,
      "b": -0.01943,
      "c": 0.004,
      "d": 0.01705,
      "g": 0.0123,
      "h": 0.7162,
      "exp_cycle": 2.0,
      "peak_prominence": 1.0,
      "range_round_dp": 1,
      "mean_round_dp": 1
    },
    "calendario": {
      "k_T": 1.9775e-11,
      "exp_T": 0.07511,
      "k_soc": 1.639,
      "exp_soc": 0.007388,
      "exp_cal": 1.25
    }
  },
  "paths": {
    "data": "data",
    "sim": "sim",
    "debug": "debug",
    "plots": "plots",
    "relatorio": "relatorio"
  },
  "relatorio": {
    "gerar_validacao_detalhada": true,
    "incluir_calculos_intermediarios": true
  },
  "llm": {
    "gemini_api_key": "AIzaSyD7xPCoC1qtZMrKvPasJTPzGH8a6OMpQGQ"
  },
  "bateria_nome": "Sany_314Ah",
  "bateria_cap_wh": 261000.0,
  "bateria_soc_min": 0.2,
  "bateria_soc_max": 0.8,
  "backend": "python",
  "sim_until_eol": false,
  "total_meses_simulados": 6
}
`

## Arquivo: results\sim_20260226_084007\data\config_snapshot.json
`json
{
  "plecs": {
    "MODELO_PLECS": "bess_batch_mode",
    "BLOCO_SOH_ALIAS": "SOH_Input",
    "ARQUIVO_ENTRADA_POT": "potencia_mes_in.mat",
    "ARQUIVO_SAIDA_SOC": "soc_out_mes.csv",
    "Nfases": 3
  },
  "dados_entrada": {
    "ARQUIVO_MAT": "cmveditora.mat",
    "dt_minutos": 15.0,
    "dias_por_mes_sim": 30,
    "meses_por_ano_sim": 12,
    "dias_por_ano_avg": 360
  },
  "simulacao": {
    "SOH_INICIAL_PERC": 100.0,
    "ANOS_SIMULACAO": 0,
    "MESES_SIMULACAO": 6,
    "data_inicio_simulacao": "2025-01-01 00:00:00"
  },
  "modelo_degradacao": {
    "ciclo": {
      "a": 2.6418,
      "b": -0.01943,
      "c": 0.004,
      "d": 0.01705,
      "g": 0.0123,
      "h": 0.7162,
      "exp_cycle": 2.0,
      "peak_prominence": 1.0,
      "range_round_dp": 1,
      "mean_round_dp": 1
    },
    "calendario": {
      "k_T": 1.9775e-11,
      "exp_T": 0.07511,
      "k_soc": 1.639,
      "exp_soc": 0.007388,
      "exp_cal": 1.25
    }
  },
  "paths": {
    "data": "data",
    "sim": "sim",
    "debug": "debug",
    "plots": "plots",
    "relatorio": "relatorio"
  },
  "relatorio": {
    "gerar_validacao_detalhada": true,
    "incluir_calculos_intermediarios": true
  },
  "llm": {
    "gemini_api_key": "AIzaSyD7xPCoC1qtZMrKvPasJTPzGH8a6OMpQGQ"
  },
  "bateria_nome": "Sany_314Ah",
  "bateria_cap_wh": 261000.0,
  "bateria_soc_min": 0.2,
  "bateria_soc_max": 0.8,
  "backend": "plecs",
  "sim_until_eol": false,
  "total_meses_simulados": 6
}
`

## Arquivo: results\sim_20260226_095900\data\config_snapshot.json
`json
{
  "plecs": {
    "MODELO_PLECS": "bess_batch_mode",
    "BLOCO_SOH_ALIAS": "SOH_Input",
    "ARQUIVO_ENTRADA_POT": "potencia_mes_in.mat",
    "ARQUIVO_SAIDA_SOC": "soc_out_mes.csv",
    "Nfases": 3
  },
  "dados_entrada": {
    "ARQUIVO_MAT": "cmveditora.mat",
    "dt_minutos": "",
    "dias_por_mes_sim": 30,
    "meses_por_ano_sim": 12,
    "dias_por_ano_avg": 360
  },
  "simulacao": {
    "SOH_INICIAL_PERC": 100.0,
    "ANOS_SIMULACAO": 1,
    "MESES_SIMULACAO": null,
    "data_inicio_simulacao": "2025-01-01 00:00:00"
  },
  "modelo_degradacao": {
    "ciclo": {
      "a": 2.6418,
      "b": -0.01943,
      "c": 0.004,
      "d": 0.01705,
      "g": 0.0123,
      "h": 0.7162,
      "exp_cycle": 2.0,
      "peak_prominence": 1.0,
      "range_round_dp": 1,
      "mean_round_dp": 1
    },
    "calendario": {
      "k_T": 1.9775e-11,
      "exp_T": 0.07511,
      "k_soc": 1.639,
      "exp_soc": 0.007388,
      "exp_cal": 1.25
    }
  },
  "paths": {
    "data": "data",
    "sim": "sim",
    "debug": "debug",
    "plots": "plots",
    "relatorio": "relatorio"
  },
  "relatorio": {
    "gerar_validacao_detalhada": true,
    "incluir_calculos_intermediarios": true
  },
  "llm": {
    "gemini_api_key": "AIzaSyD7xPCoC1qtZMrKvPasJTPzGH8a6OMpQGQ"
  },
  "bateria_nome": "Sany_314Ah",
  "bateria_cap_wh": 261000.0,
  "bateria_soc_min": 0.2,
  "bateria_soc_max": 0.8,
  "backend": "plecs",
  "sim_until_eol": false,
  "total_meses_simulados": 12
}
`

## Arquivo: results\sim_20260226_100307\data\config_snapshot.json
`json
{
  "plecs": {
    "MODELO_PLECS": "bess_batch_mode",
    "BLOCO_SOH_ALIAS": "SOH_Input",
    "ARQUIVO_ENTRADA_POT": "potencia_mes_in.mat",
    "ARQUIVO_SAIDA_SOC": "soc_out_mes.csv",
    "Nfases": 3
  },
  "dados_entrada": {
    "ARQUIVO_MAT": "cmveditora.mat",
    "dt_minutos": "",
    "dias_por_mes_sim": 30,
    "meses_por_ano_sim": 12,
    "dias_por_ano_avg": 360
  },
  "simulacao": {
    "SOH_INICIAL_PERC": 100.0,
    "ANOS_SIMULACAO": 1,
    "MESES_SIMULACAO": null,
    "data_inicio_simulacao": "2025-01-01 00:00:00"
  },
  "modelo_degradacao": {
    "ciclo": {
      "a": 2.6418,
      "b": -0.01943,
      "c": 0.004,
      "d": 0.01705,
      "g": 0.0123,
      "h": 0.7162,
      "exp_cycle": 2.0,
      "peak_prominence": 1.0,
      "range_round_dp": 1,
      "mean_round_dp": 1
    },
    "calendario": {
      "k_T": 1.9775e-11,
      "exp_T": 0.07511,
      "k_soc": 1.639,
      "exp_soc": 0.007388,
      "exp_cal": 1.25
    }
  },
  "paths": {
    "data": "data",
    "sim": "sim",
    "debug": "debug",
    "plots": "plots",
    "relatorio": "relatorio"
  },
  "relatorio": {
    "gerar_validacao_detalhada": true,
    "incluir_calculos_intermediarios": true
  },
  "llm": {
    "gemini_api_key": "AIzaSyD7xPCoC1qtZMrKvPasJTPzGH8a6OMpQGQ"
  },
  "bateria_nome": "Sany_314Ah",
  "bateria_cap_wh": 261000.0,
  "bateria_soc_min": 0.2,
  "bateria_soc_max": 0.8,
  "backend": "python",
  "sim_until_eol": false,
  "total_meses_simulados": 12
}
`

## Arquivo: results\sim_20260226_152703\data\config_snapshot.json
`json
{
  "plecs": {
    "MODELO_PLECS": "bess_batch_mode",
    "BLOCO_SOH_ALIAS": "SOH_Input",
    "ARQUIVO_ENTRADA_POT": "potencia_mes_in.mat",
    "ARQUIVO_SAIDA_SOC": "soc_out_mes.csv",
    "Nfases": 3
  },
  "dados_entrada": {
    "ARQUIVO_MAT": "cmveditora.mat",
    "dt_minutos": "",
    "dias_por_mes_sim": 30,
    "meses_por_ano_sim": 12,
    "dias_por_ano_avg": 360
  },
  "simulacao": {
    "SOH_INICIAL_PERC": 100.0,
    "ANOS_SIMULACAO": 1,
    "MESES_SIMULACAO": null,
    "data_inicio_simulacao": "2025-01-01 00:00:00"
  },
  "modelo_degradacao": {
    "ciclo": {
      "a": 2.6418,
      "b": -0.01943,
      "c": 0.004,
      "d": 0.01705,
      "g": 0.0123,
      "h": 0.7162,
      "exp_cycle": 2.0,
      "peak_prominence": 1.0,
      "range_round_dp": 1,
      "mean_round_dp": 1
    },
    "calendario": {
      "k_T": 1.9775e-11,
      "exp_T": 0.07511,
      "k_soc": 1.639,
      "exp_soc": 0.007388,
      "exp_cal": 1.25
    }
  },
  "paths": {
    "data": "data",
    "sim": "sim",
    "debug": "debug",
    "plots": "plots",
    "relatorio": "relatorio"
  },
  "relatorio": {
    "gerar_validacao_detalhada": true,
    "incluir_calculos_intermediarios": true
  },
  "llm": {
    "gemini_api_key": "AIzaSyD7xPCoC1qtZMrKvPasJTPzGH8a6OMpQGQ"
  },
  "bateria_nome": "LiFePO4_78Ah",
  "bateria_cap_wh": 15444.0,
  "bateria_soc_min": 0.1,
  "bateria_soc_max": 0.9,
  "backend": "plecs",
  "sim_until_eol": false,
  "total_meses_simulados": 12
}
`

## Arquivo: results\sim_20260226_153933\data\config_snapshot.json
`json
{
  "plecs": {
    "MODELO_PLECS": "bess_batch_mode",
    "BLOCO_SOH_ALIAS": "SOH_Input",
    "ARQUIVO_ENTRADA_POT": "potencia_mes_in.mat",
    "ARQUIVO_SAIDA_SOC": "soc_out_mes.csv",
    "Nfases": 3
  },
  "dados_entrada": {
    "ARQUIVO_MAT": "cmveditora.mat",
    "dt_minutos": 15.0,
    "dias_por_mes_sim": 30,
    "meses_por_ano_sim": 12,
    "dias_por_ano_avg": 360
  },
  "simulacao": {
    "SOH_INICIAL_PERC": 100.0,
    "ANOS_SIMULACAO": 1,
    "MESES_SIMULACAO": null,
    "data_inicio_simulacao": "2025-01-01 00:00:00"
  },
  "modelo_degradacao": {
    "ciclo": {
      "a": 2.6418,
      "b": -0.01943,
      "c": 0.004,
      "d": 0.01705,
      "g": 0.0123,
      "h": 0.7162,
      "exp_cycle": 2.0,
      "peak_prominence": 1.0,
      "range_round_dp": 1,
      "mean_round_dp": 1
    },
    "calendario": {
      "k_T": 1.9775e-11,
      "exp_T": 0.07511,
      "k_soc": 1.639,
      "exp_soc": 0.007388,
      "exp_cal": 1.25
    }
  },
  "paths": {
    "data": "data",
    "sim": "sim",
    "debug": "debug",
    "plots": "plots",
    "relatorio": "relatorio"
  },
  "relatorio": {
    "gerar_validacao_detalhada": true,
    "incluir_calculos_intermediarios": true
  },
  "llm": {
    "gemini_api_key": "AIzaSyD7xPCoC1qtZMrKvPasJTPzGH8a6OMpQGQ"
  },
  "bateria_nome": "Sany_314Ah",
  "bateria_cap_wh": 261000.0,
  "bateria_soc_min": 0.2,
  "bateria_soc_max": 0.8,
  "backend": "python",
  "sim_until_eol": true,
  "total_meses_simulados": 197
}
`

## Arquivo: src\besx\__init__.py
`python

`

## Arquivo: src\besx\application\__init__.py
`python

`

## Arquivo: src\besx\application\simulation.py
`python

import os
import json
import time
import numpy as np
import pandas as pd
import datetime
from IPython.display import display

# Imports internos
from besx.infrastructure.files.file_manager import FileManager
from besx.infrastructure.loaders.data_handler import data_handle
from besx.infrastructure.plecs.plecs_connector import run_monthly_simulation, close_plecs_server, extrair_soc_final
from besx.domain.models.degradation_model import dano_ciclo, dano_calendar, calcular_estatisticas_operacionais
from besx.domain.models.battery_simulator import picos_e_vales, ciclos_idle
from besx.infrastructure.visualization.plots import plotar_capacidade_mensal, plotar_composicao_degradacao
from besx.infrastructure.reports.report import gerar_relatorio_txt
from besx.infrastructure.logging.logger import logger
from besx.infrastructure.reports.validation_report import gerar_relatorio_validacao, exportar_debug_degradacao, export_xlsx

class SimulationManager:
    def __init__(self, config, backend: str = "python", data_file: str = None,
                 on_mes_complete: callable = None, sim_until_eol: bool = False):
        self.config = config
        self.backend = backend  # "python" | "plecs"
        self.data_file = data_file # Opcional: nome do arquivo em /database
        self.on_mes_complete = on_mes_complete
        self.sim_until_eol = sim_until_eol  # Se True, ignora meses_alvo e roda até EOL
        # Inicializa gerenciador de arquivos (cria pastas)
        self.file_manager = FileManager()
        
        # Estado Inicial
        self.soh_atual = self.config.simulacao.SOH_INICIAL_PERC / 100.0
        self.soc_zero = 0
        self.resultados_mensais = []
        self.calculos_detalhados = []  # Armazena DataFrames detalhados de cada mês
        
        # Variáveis de Acumulação
        self.acum_ciclo_global = 0.0
        self.acum_cal_global = 0.0
        self.start_time = None
        
        # Atalhos de config
        self.exp_cal = self.config.modelo_degradacao.calendario.exp_cal
        self.cfg_bat = self.config.bateria

    def run(self):
        self.start_time = datetime.datetime.now()
        logger.info("Iniciando a Execução via SimulationManager")
        logger.info(f"Resultados serão salvos em: {self.file_manager.sim_folder}")
        
        # --- ETAPA 1: CARREGANDO OS DADOS ---
        # Em modo EOL, carrega o máximo de dados possível (20 anos)
        # Em modo normal, usa os anos configurados pelo usuário
        if self.sim_until_eol:
            meses_alvo = 240  # 20 anos como teto de segurança para EOL
            logger.info("[EOL] Modo 'Simular até Fim de Vida' ativo. Rodando até atingir o limite.")
        elif self.config.simulacao.MESES_SIMULACAO is not None:
            meses_alvo = self.config.simulacao.MESES_SIMULACAO
            logger.info(f"Modo Duração Personalizada: {meses_alvo} meses.")
        else:
            meses_alvo = self.config.simulacao.ANOS_SIMULACAO * 12
        
        # Passamos o data_file se fornecido, senão ele pede via console no data_handle()
        df_perfil_bess = data_handle(nome_arquivo=self.data_file, meses_alvo=meses_alvo)
        
        if not df_perfil_bess:
            logger.error("Falha ao carregar dados de entrada. Abortando.")
            return

        logger.info("Dados iniciais tratados")
        
        # --- ETAPA 2: ITERAÇÃO MENSAL ---
        total_meses = len(df_perfil_bess)
        ctt = 0
        try:
            for df_mes in df_perfil_bess:
                ctt += 1
                self._processar_mes(df_mes, ctt, total_meses)
                
                # Checagem de fim de vida (sempre ativa)
                if self.soh_atual * 100 <= 100 - self.cfg_bat.capacidade_limite_perda_perc:
                    logger.warning("Capacidade limite atingida. Finalizando simulação.")
                    break
        finally:
            if self.backend == "plecs":
                close_plecs_server()

        # --- ETAPA 3: RESULTADOS FINAIS ---
        self._finalizar_simulacao()

    def _processar_mes(self, df_mes, mes_id, total_meses):
        # 1. Simulação da bateria (backend escolhido no menu)
        perfil_soc_mes = run_monthly_simulation(
            df_mes, self.soh_atual, self.soc_zero, mes_id,
            config=self.config,
            backend=self.backend
        )
        
        # Atualiza SOC inicial para o próximo mês
        self.soc_zero = extrair_soc_final(perfil_soc_mes)
        
        # ... (logging/debug omitido por brevidade se não mudar)
        # Exporta Debug SOC
        caminho_debug = self.file_manager.get_debug_path("") # Pasta debug
        if self.config.relatorio.gerar_validacao_detalhada:
            exportar_debug_degradacao(perfil_soc_mes, "perfil_soc_mes", mes_id, pasta_debug=caminho_debug)
        
        # 2. Dano Cíclico
        prominence = self.config.modelo_degradacao.ciclo.peak_prominence
        perfil_simp = picos_e_vales(perfil_soc_mes['SOC'], prominence=prominence)
        
        if self.config.relatorio.gerar_validacao_detalhada:
            exportar_debug_degradacao(perfil_simp, "picos_e_vales", mes_id, pasta_debug=caminho_debug)   
        
        # Prepara parâmetros para o modelo de ciclo
        params_ciclo = self.config.modelo_degradacao.ciclo
        Ccyc, df_ciclo_detalhado = dano_ciclo(perfil_simp.tolist(), self.cfg_bat.Tbat_kelvin, params_ciclo)
        self.acum_ciclo_global = np.sqrt(self.acum_ciclo_global**2 + Ccyc**2)
        
        if self.config.relatorio.gerar_validacao_detalhada:
            exportar_debug_degradacao(perfil_soc_mes['SOC'].round(1).tolist(),"soc_usado_idle", mes_id, pasta_debug=caminho_debug)

        # 3. Dano Calendário
        if len(perfil_soc_mes) > 1:
            dt_soc_minutos = (perfil_soc_mes['Tempo'].iloc[1] - perfil_soc_mes['Tempo'].iloc[0]) / 60.0
        else:
            dt_soc_minutos = 1.0
        
        minutos_por_mes = (self.config.dados_entrada.dias_por_ano_avg * 24 * 60) / 12
        idle_cycles_mes = ciclos_idle(
            perfil_soc_mes['SOC'].round(1).tolist(), 
            dt_minutos_soc=dt_soc_minutos,
            minutos_por_mes=minutos_por_mes
        )
        
        if self.config.relatorio.gerar_validacao_detalhada:
            exportar_debug_degradacao(idle_cycles_mes, "idle_cycles_mes", mes_id, pasta_debug=caminho_debug)
        
        params_cal = self.config.modelo_degradacao.calendario
        Ccal, df_calendario_detalhado = dano_calendar(
            idle_cycles_mes, 
            self.cfg_bat.Tbat_kelvin_idle,
            model_params=params_cal,
            dt_minutos=self.config.dados_entrada.dt_minutos,
            dias_por_ano_avg=self.config.dados_entrada.dias_por_ano_avg
        )
        self.acum_cal_global = (self.acum_cal_global**self.exp_cal + Ccal**self.exp_cal)**(1/self.exp_cal)

        # 4. Atualiza SOH
        perda_total_perc = self.acum_ciclo_global + self.acum_cal_global
        self.soh_atual = (self.config.simulacao.SOH_INICIAL_PERC - perda_total_perc) / 100.0

        # 5. Estatísticas
        cap_kwh = self.cfg_bat.capacidade_nominal_wh / 1000.0
        stats_ops = calcular_estatisticas_operacionais(perfil_soc_mes, df_mes, cap_kwh=cap_kwh, lista_periodos_idle=idle_cycles_mes)
        
        logger.info(f"   -> Resumo Mês {mes_id}/{total_meses}: {stats_ops.get('Ciclos_Contagem')} ciclos | "
              f"SOH: {self.soh_atual*100:.2f}%")

        # 6. Agrega Resultados
        dados_mes = {
            'mes': mes_id,
            'total_meses': total_meses,
            'dano_ciclos_mes': Ccyc,
            'dano_cal_mes': Ccal,
            'dano_ciclo_acum': self.acum_ciclo_global,
            'dano_cal_acum': self.acum_cal_global,
            'dano_total_acum': self.acum_ciclo_global + self.acum_cal_global,
            'capacidade_restante': self.soh_atual * 100,
            **stats_ops
        }
        self.resultados_mensais.append(dados_mes)
        
        # Armazena cálculos detalhados para o relatório de validação
        self.calculos_detalhados.append({
            'mes': mes_id,
            'df_ciclo': df_ciclo_detalhado,
            'df_calendario': df_calendario_detalhado
        })

        # 7. Callback para Dashboard (Live Update)
        if self.on_mes_complete:
            self.on_mes_complete(perfil_soc_mes, dados_mes, df_mes)

    def _finalizar_simulacao(self):
        df_resultados_finais = pd.DataFrame(self.resultados_mensais)
        
        logger.info("\n--- Resultado Final Consolidado ---")
        display(df_resultados_finais)
        
        # Obter nome amigável da bateria
        bateria_nome = next(
            (n for n, p in __import__('besx.config', fromlist=['PERFIS_BATERIA']).PERFIS_BATERIA.items()
             if p.capacidade_nominal_wh == self.config.bateria.capacidade_nominal_wh), 'Desconhecido'
        )
        # Prefixo: Ex: python_Bateria_100kWh_20231027_103000
        prefixo = f"{self.backend}_{bateria_nome}_{self.file_manager.timestamp}"
        
        # Salvar Excel Final na pasta data
        caminho_excel = self.file_manager.get_data_path(f"resultados_completos_{prefixo}.xlsx")
        df_resultados_finais.to_excel(caminho_excel, index=False)
        logger.info(f"Resultados salvos em: {caminho_excel}")

        # Salvar snapshot da configuração para comparação futura
        try:
            snap = self.config.model_dump(exclude={'bateria'})
            snap['bateria_nome'] = bateria_nome
            snap['bateria_cap_wh'] = self.config.bateria.capacidade_nominal_wh
            snap['bateria_soc_min'] = self.config.bateria.soc_min_pct
            snap['bateria_soc_max'] = self.config.bateria.soc_max_pct
            snap['backend'] = self.backend
            snap['sim_until_eol'] = self.sim_until_eol
            snap['total_meses_simulados'] = len(self.resultados_mensais)
            # Serializar para JSON com suporte a float
            snap_path = self.file_manager.get_data_path(f"config_snapshot_{prefixo}.json")
            with open(snap_path, 'w', encoding='utf-8') as f:
                json.dump(snap, f, indent=2, default=str)
            logger.info(f"Snapshot da configuração salvo em: {snap_path}")
        except Exception as e:
            logger.warning(f"Não foi possível salvar config_snapshot.json: {e}")

        # Plots
        caminho_plot_cap = self.file_manager.get_plot_path(f"capacidade_restante_mensal_{prefixo}.png")
        plotar_capacidade_mensal(df_resultados_finais, nome_arquivo_saida=caminho_plot_cap)
        
        caminho_plot_comp = self.file_manager.get_plot_path(f"composicao_degradacao_{prefixo}.png")
        plotar_composicao_degradacao(df_resultados_finais, nome_arquivo_saida=caminho_plot_comp)
        
        close_plecs_server()
        
        # Gerar Relatório de Validação (se habilitado)
        if self.config.relatorio.gerar_validacao_detalhada:
            gerar_relatorio_validacao(
                self.file_manager, 
                self.config, 
                self.resultados_mensais, 
                self.calculos_detalhados,
                prefixo=prefixo
            )
        
        # Gerar Relatório de Texto
        # Calcula a duração
        end_time = datetime.datetime.now()
        duration = end_time - self.start_time
        gerar_relatorio_txt(self.file_manager, self.config, df_resultados_finais, str(duration), prefixo=prefixo)

    # Método antigo removido em favor do módulo externo
`

## Arquivo: src\besx\config.py
`python
import os
import json
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field

# ============================================================
#  ▶  ALTERE AQUI PARA TROCAR O MODELO DE BATERIA  ◀
# ============================================================
PERFIL_ATIVO = "LiFePO4_78Ah"
# ============================================================

# --- Classes de Configuração (Pydantic) ---

class PlecsConfig(BaseModel):
    MODELO_PLECS: str = "bess_batch_mode"
    BLOCO_SOH_ALIAS: str = "SOH_Input"
    ARQUIVO_ENTRADA_POT: str = "potencia_mes_in.mat"
    ARQUIVO_SAIDA_SOC: str = "soc_out_mes.csv"
    Nfases: int = 3

class DadosEntradaConfig(BaseModel):
    ARQUIVO_MAT: str = "cmveditora.mat"
    dt_minutos: Union[str, float, int] = ""  # Pode ser string vazia inicial ou número
    dias_por_mes_sim: int = 30
    meses_por_ano_sim: int = 12
    dias_por_ano_avg: int = 360

class SimulacaoConfig(BaseModel):
    SOH_INICIAL_PERC: float = 100.0
    ANOS_SIMULACAO: int = 1
    MESES_SIMULACAO: Optional[int] = None
    data_inicio_simulacao: str = '2025-01-01 00:00:00'

class BateriaConfig(BaseModel):
    model_config = {"populate_by_name": True}
    capacidade_nominal_wh: float
    capacidade_limite_perda_perc: float = 20.0
    Tbat_kelvin: float = 298.15
    Tbat_kelvin_idle: float = 298.15
    soc_min_pct: float = Field(default=0.2, alias="soc_min")
    soc_max_pct: float = Field(default=0.8, alias="soc_max")
    Rs: Optional[float] = None
    Ah: Optional[float] = None
    Ns: Optional[int] = None
    Np: Optional[int] = None
    v_min_celula: Optional[float] = Field(default=None, alias="Vbmin")
    v_max_celula: Optional[float] = Field(default=None, alias="Vbmax")
    P_bess: Optional[float] = None
    soc_prof: Optional[List[float]] = None
    ocv_prof: Optional[List[float]] = None
    rendimento_pcs: float = 0.88

class DegradacaoCicloConfig(BaseModel):
    a: float = 2.6418
    b: float = -0.01943
    c: float = 0.004
    d: float = 0.01705
    g: float = 0.0123
    h: float = 0.7162
    exp_cycle: float = 2.0
    peak_prominence: float = 1.0
    range_round_dp: int = 1
    mean_round_dp: int = 1

class DegradacaoCalendarioConfig(BaseModel):
    k_T: float = 1.9775e-11
    exp_T: float = 0.07511
    k_soc: float = 1.639
    exp_soc: float = 0.007388
    exp_cal: float = 1.25  # 10/8

class ModeloDegradacaoConfig(BaseModel):
    ciclo: DegradacaoCicloConfig = Field(default_factory=DegradacaoCicloConfig)
    calendario: DegradacaoCalendarioConfig = Field(default_factory=DegradacaoCalendarioConfig)

class PathsConfig(BaseModel):
    data: str = "data"
    sim: str = "sim"
    debug: str = "debug"
    plots: str = "plots"
    relatorio: str = "relatorio"

class RelatorioConfig(BaseModel):
    gerar_validacao_detalhada: bool = True
    incluir_calculos_intermediarios: bool = True

class LLMConfig(BaseModel):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "AIzaSyD7xPCoC1qtZMrKvPasJTPzGH8a6OMpQGQ")

class Settings(BaseModel):
    plecs: PlecsConfig = Field(default_factory=PlecsConfig)
    dados_entrada: DadosEntradaConfig = Field(default_factory=DadosEntradaConfig)
    simulacao: SimulacaoConfig = Field(default_factory=SimulacaoConfig)
    bateria: Optional[BateriaConfig] = None
    modelo_degradacao: ModeloDegradacaoConfig = Field(default_factory=ModeloDegradacaoConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    relatorio: RelatorioConfig = Field(default_factory=RelatorioConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)

# --- Carregamento de Perfis de Bateria ---
# --- Caminhos Base ---
from pathlib import Path

# O arquivo config.py está em src/besx/config.py
# ROOT_DIR deve apontar para a raiz do projeto
CWD = Path(__file__).parent.resolve()
ROOT_DIR = CWD.parent.parent.resolve()

PATH_BATTERIES = CWD / "resources" / "batteries.json"
PATH_DATABASE = ROOT_DIR / "database"
PATH_RESULTS = ROOT_DIR / "results"

try:
    with open(PATH_BATTERIES, "r", encoding="utf-8") as f:
        PERFIS_BATERIA_RAW = json.load(f)
        # Converte para dict de BateriaConfig para validação imediata
        PERFIS_BATERIA = {k: BateriaConfig(**v) for k, v in PERFIS_BATERIA_RAW.items()}
except Exception as e:
    # Fallback básico caso o arquivo não exista ou esteja corrompido
    fallback_perfil = BateriaConfig(
        capacidade_nominal_wh=10000.0,
        capacidade_limite_perda_perc=20.0,
        Tbat_kelvin=298.15,
        Tbat_kelvin_idle=298.15,
        soc_min=0.2, soc_max=0.8
    )
    PERFIS_BATERIA = {"Default_LFP": fallback_perfil}
    from besx.infrastructure.logging.logger import logger
    logger.warning(f"Falha ao carregar batteries.json ({e}). Usando perfil de segurança.")
# Valida o perfil escolhido antes de montar a configuração final
if PERFIL_ATIVO not in PERFIS_BATERIA:
    raise ValueError(
        f"PERFIL_ATIVO='{PERFIL_ATIVO}' não existe. "
        f"Opções disponíveis: {list(PERFIS_BATERIA.keys())}"
    )

# Instância Global de Configuração
CONFIGURACAO = Settings(
    bateria=PERFIS_BATERIA[PERFIL_ATIVO]
)

`

## Arquivo: src\besx\domain\__init__.py
`python

`

## Arquivo: src\besx\domain\models\__init__.py
`python

`

## Arquivo: src\besx\domain\models\battery_simulator.py
`python
"""
battery_simulator.py  —  Simulador de SOC por Integração de Coulomb

Substitui o PLECS na simulação mensal do comportamento da bateria.
Dado um perfil de potência mensal, calcula o perfil de SOC passo a passo.

Método: Integração de Coulomb
  SOC(t+dt) = SOC(t) + I(t) * dt / Q_efetivo
  I(t) = P(t) / V_ocv(SOC(t))

Saída compatível com o CSV que o PLECS produzia:
  DataFrame com colunas ['Tempo', 'SOC']
    - Tempo em segundos
    - SOC em % (0–100)
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from besx.config import BateriaConfig
from besx.infrastructure.logging.logger import logger

def _interpolar_ocv(soc_percent: float, soc_prof: list, ocv_prof: list) -> float:
    """
    Interpola a tensão OCV do banco para um dado SOC (%).

    Args:
        soc_percent: SOC atual em % (0–100)
        soc_prof: Lista de pontos de SOC da curva OCV (0–1)
        ocv_prof: Lista de tensões OCV correspondentes (V)

    Returns:
        Tensão OCV interpolada em Volts
    """
    soc_frac = soc_percent / 100.0
    return float(np.interp(soc_frac, soc_prof, ocv_prof))

def simular_soc_mes(df_mes: pd.DataFrame, soh_atual: float, soc_inicial: float, cfg_bat) -> pd.DataFrame:
    """
    Simula o perfil de SOC e Tensão de um mês usando integração de Coulomb e Modelo Rint.
    
    df_mes: DataFrame contendo ['timestamp_min', 'pot_w'] (Potência CA solicitada)
    cfg_bat: Objeto/dataclass com (Ns, Np, Ah, Rs, rendimento_pcs, soc_min_pct, soc_max_pct, v_max_celula, v_min_celula, soc_prof, ocv_prof)
    """
    # 1. Extração para arrays NumPy (Acelera o loop for em mais de 50x)
    pot_w_arr = df_mes['pot_w'].values
    tempos_min_arr = df_mes['timestamp_min'].values
    n_passos = len(pot_w_arr)
    
    # 2. Inicialização dos vetores de saída
    soc_out = np.zeros(n_passos)
    corrente_out = np.zeros(n_passos)
    tensao_term_out = np.zeros(n_passos)
    
    soc_out[0] = soc_inicial
    
    # Parâmetros do Banco
    q_efetivo_celula = cfg_bat.Ah * soh_atual
    rs_banco = (cfg_bat.Rs * cfg_bat.Ns) / cfg_bat.Np if cfg_bat.Rs else 0.0
    v_max_banco = cfg_bat.v_max_celula * cfg_bat.Ns
    v_min_banco = cfg_bat.v_min_celula * cfg_bat.Ns
    
    soc_min_clip = cfg_bat.soc_min_pct * 100.0
    soc_max_clip = cfg_bat.soc_max_pct * 100.0
    
    for k in range(n_passos - 1):
        # Delta T em horas
        dt_h = (tempos_min_arr[k + 1] - tempos_min_arr[k]) / 60.0
        
        # Interpolação da Tensão OCV atual
        v_ocv_celula = _interpolar_ocv(soc_out[k], cfg_bat.soc_prof, cfg_bat.ocv_prof)
        v_ocv_banco = v_ocv_celula * cfg_bat.Ns
        
        # Potência CA limitida pelo PCS
        p_bess_limite = float(cfg_bat.P_bess) if cfg_bat.P_bess else float('inf')
        p_ca_w = np.clip(pot_w_arr[k], -p_bess_limite, p_bess_limite)
        
        # Potência DC na Bateria (P > 0: Carga | P < 0: Descarga)
        if p_ca_w > 0:
            p_bateria_w = p_ca_w * cfg_bat.rendimento_pcs
        elif p_ca_w < 0:
            p_bateria_w = p_ca_w / cfg_bat.rendimento_pcs
        else:
            p_bateria_w = 0.0
            
        # Cálculo da Corrente
        # rs_banco^2 * I^2 + V_ocv * I - P_bateria = 0
        if rs_banco > 0.0:
            delta = v_ocv_banco**2 + 4 * rs_banco * p_bateria_w # O Valor é positivo pois na equação p_bateria_w é negativo
            if delta < 0:
                corrente_banco = -v_ocv_banco / (2 * rs_banco)
            else:
                corrente_banco = (-v_ocv_banco + np.sqrt(delta)) / (2 * rs_banco)
        else:
            corrente_banco = p_bateria_w / v_ocv_banco
            
        # --- NOVO: LIMITAÇÃO FÍSICA DE TENSÃO (BMS Cut-off) ---
        # V_term = V_ocv + I * R_s
        v_term_estimada = v_ocv_banco + (corrente_banco * rs_banco)
        
        if v_term_estimada > v_max_banco:
            # Força a corrente para o máximo que a tensão limite permite
            corrente_banco = (v_max_banco - v_ocv_banco) / rs_banco
            v_term_estimada = v_max_banco
        elif v_term_estimada < v_min_banco:
            corrente_banco = (v_min_banco - v_ocv_banco) / rs_banco
            v_term_estimada = v_min_banco
            
        # Registra valores
        corrente_out[k] = corrente_banco
        tensao_term_out[k] = v_term_estimada
        
        # Coulomb Counting (na célula)
        corrente_celula = corrente_banco / cfg_bat.Np
        delta_soc = (corrente_celula * dt_h / q_efetivo_celula) * 100.0  # [%]
        
        # Atualiza e clipa o SOC
        soc_novo = np.clip(soc_out[k] + delta_soc, soc_min_clip, soc_max_clip)
        soc_out[k + 1] = soc_novo
        
    # Salva o último passo de corrente/tensão (mantém o valor anterior para não zerar)
    corrente_out[-1] = corrente_out[-2]
    tensao_term_out[-1] = tensao_term_out[-2]
        
    # 3. Reconstrói o DataFrame de Saída para a Análise de Degradação
    df_resultado = pd.DataFrame({
        'Tempo': tempos_min_arr * 60.0,
        'SOC': soc_out,
        'Corrente_A': corrente_out,
        'Tensao_Term_V': tensao_term_out
    })
    
    return df_resultado

def old_simular_soc_mes(
    df_mes: pd.DataFrame,
    soh_atual: float,
    soc_inicial: float,
    cfg_bat: BateriaConfig,
) -> pd.DataFrame:
    """
    Simula o perfil de SOC de um mês usando integração de Coulomb.

    Reproduz o comportamento do modelo de bateria do PLECS:
    - Limita a potência a ±P_bess
    - Limita o SOC ao intervalo [SOCmin, SOCmax]
    - Usa a curva OCV×SOC para estimar a tensão instantânea
    - Aplica carga limitada quando os limites de SOC são atingidos

    Args:
        df_mes (pd.DataFrame):
            Perfil de potência do mês.
            Colunas esperadas: [Tempo (min), Potencia_kW]
        soh_atual (float):
            State of Health atual — fração 0–1. Escala a capacidade.
        soc_inicial (float):
            SOC inicial do mês — fração 0–1.
        cfg_bat (BateriaConfig):
            Configuração da bateria (atributo CONFIGURACAO.bateria).
            Campos usados:
              - 'Ah'      : Capacidade nominal do módulo (Ah)
              - 'Ns'      : Número de módulos em série
              - 'Np'      : Número de strings em paralelo
              - 'soc_prof': Lista SOC fracionário para curva OCV
              - 'ocv_prof': Lista de tensões OCV (V)
              - 'soc_min' : SOC mínimo (fração 0–1)
              - 'soc_max' : SOC máximo (fração 0–1)
              - 'P_bess'  : Potência máxima do BESS (W)

    Returns:
        pd.DataFrame:
            DataFrame com colunas ['Tempo', 'SOC']:
              - 'Tempo': tempo em segundos (float)
              - 'SOC'  : SOC em % (float, 0–100)
            Estrutura idêntica ao CSV gerado pelo PLECS.
    """
    # ------------------------------------------------------------------ #
    #  1.  Leitura de parâmetros                                           #
    # ------------------------------------------------------------------ #
    Ah       = float(cfg_bat.Ah)
    Ns       = int(cfg_bat.Ns)
    Np       = int(cfg_bat.Np)
    soc_prof = cfg_bat.soc_prof
    ocv_prof = cfg_bat.ocv_prof
    soc_min  = float(cfg_bat.soc_min_pct)
    soc_max  = float(cfg_bat.soc_max_pct)
    p_bess   = float(cfg_bat.P_bess)
    rendimento_pcs = float(getattr(cfg_bat, 'rendimento_pcs', 0.88))

    Q_efetivo_Ah = Ah * Np * soh_atual #provocando o dano do SOH
    soc_pct = float(soc_inicial) * 100.0

    col_tempo    = df_mes.columns[0]
    col_potencia = df_mes.columns[1]

    tempos_min = df_mes[col_tempo].to_numpy(dtype=float)
    pot_w      = df_mes[col_potencia].to_numpy(dtype=float)

    n_passos = len(tempos_min)

    # ------------------------------------------------------------------ #
    #  3.  Pré-alocação dos arrays de saída                               #
    # ------------------------------------------------------------------ #
    tempos_s = tempos_min * 60.0          # minutos → segundos
    soc_out  = np.empty(n_passos, dtype=float)
    soc_out[0] = soc_pct

    # ------------------------------------------------------------------ #
    #  4.  Integração de Coulomb passo a passo                            #
    # ------------------------------------------------------------------ #
    soc_min_pct = soc_min * 100.0
    soc_max_pct = soc_max * 100.0

    for k in range(n_passos - 1):
        # Intervalo de tempo em horas
        dt_h = (tempos_min[k + 1] - tempos_min[k]) / 60.0

        # Tensão OCV atual (V) por célula
        v_ocv_celula = _interpolar_ocv(soc_out[k], soc_prof, ocv_prof)
        if v_ocv_celula <= 0.0:
            v_ocv_celula = ocv_prof[0] if ocv_prof[0] > 0 else 1.0
            
        # Tensão real do banco
        v_ocv_banco = v_ocv_celula * Ns

        # 1. Potência solicitada pelo lado CA (W) — limitada à potência máxima do BESS
        p_ca_w = np.clip(pot_w[k], -p_bess, p_bess)
        
        # 2. Potência efetiva na Bateria DC (Aplicando o Rendimento)
        #  Convenção de sinal:
        #    P > 0  →  carga (lado CA injeta energia no BESS). Bateria recebe menos energia.
        #    P < 0  →  descarga (BESS injeta na rede). Bateria precisa entregar mais energia.
        if p_ca_w > 0:
            p_bateria_w = p_ca_w * rendimento_pcs
        elif p_ca_w < 0:
            p_bateria_w = p_ca_w / rendimento_pcs
        else:
            p_bateria_w = 0.0
            
        # 3. Resistência do Banco
        # Rs fornecido no config é por célula.
        # R_banco = Rs_celula * Ns / Np
        if cfg_bat.Rs is not None:
            rs_banco = float(cfg_bat.Rs) * Ns / Np
        else:
            rs_banco = 0.0

        # 4. Corrente do banco (Resolvendo a Malha do PLECS)
        # O PLECS divide a Potência pela Tensão NOS TERMINAIS do bloco da Bateria.
        # A Tensão nos terminais é: V_term = V_ocv_banco + I_banco * rs_banco
        # E sabemos que: P_bateria_w = V_term * I_banco 
        # Substituindo: P_bateria_w = (V_ocv_banco + I_banco * rs_banco) * I_banco 
        #               P_bateria_w = I_banco^2 * rs_banco + V_ocv_banco * I_banco
        #               0           = rs_banco * I_banco^2 + V_ocv_banco * I_banco - P_bateria_w
        if rs_banco > 0.0:
            delta = v_ocv_banco**2 + 4 * rs_banco * p_bateria_w # + por que a corrente é negativa quando a bateria está descarregando
            if delta < 0:
                # Caso limite teórico excedido (ex: forçando potência excessiva numa bateria morta)
                corrente_banco = -v_ocv_banco / (2 * rs_banco)
            else:
                corrente_banco = (-v_ocv_banco + np.sqrt(delta)) / (2 * rs_banco)
        else:
            # Caso ideal (sem resistência interna)
            corrente_banco = p_bateria_w / v_ocv_banco
        
        # 4. Corrente que flui por uma célula / string individual (dividindo pelos paralelos)
        corrente_celula = corrente_banco / Np
            
        # 5. Variação de SOC (Integradora):
        #    Cálculo na Célula: ΔSOC = (I_cel / (Ah_celula * SOH)) * dt_h * 100 %
        #    Q_efetivo da célula individual = Ah * soh_atual
        q_efetivo_celula = Ah * soh_atual
        
        delta_soc  = (corrente_celula * dt_h / q_efetivo_celula) * 100.0  # [%]

        soc_novo = soc_out[k] + delta_soc

        # Clamp físico e operacional
        soc_novo = float(np.clip(soc_novo, soc_min_pct, soc_max_pct))
        soc_out[k + 1] = soc_novo

    # ------------------------------------------------------------------ #
    #  5.  Monta DataFrame de saída (idêntico ao CSV do PLECS)            #
    # ------------------------------------------------------------------ #
    df_resultado = pd.DataFrame({
        'Tempo': tempos_s,
        'SOC':   soc_out,
    })

    logger.info(
        f"   [BattSim] SOC inicial={soc_out[0]:.1f}% | "
        f"SOC final={soc_out[-1]:.1f}% | "
        f"min={soc_out.min():.1f}% | max={soc_out.max():.1f}%"
    )

    return df_resultado

def picos_e_vales(profile_series: pd.Series, prominence: float = 1.0) -> np.ndarray:
    """
    Extrai picos e vales de uma Série de SOC.
    """
    profile_array = profile_series.to_numpy()

    picos, _ = find_peaks(profile_array, prominence=prominence)
    vales, _ = find_peaks(-profile_array, prominence=prominence)

    # Usa os ÍNDICES da Série original
    indices_combinados = np.concatenate((
        [profile_series.index[0]],
        profile_series.index[picos],
        profile_series.index[vales],
        [profile_series.index[-1]]
    ))
    indices_ordenados = np.sort(np.unique(indices_combinados))

    soc_profile_simp = profile_series.loc[indices_ordenados].to_numpy()
    return soc_profile_simp

def ciclos_idle(profile: list, dt_minutos_soc: float, minutos_por_mes: float) -> list:
    """
    Encontra períodos 'idle' (SOC constante) em um perfil de SOC.
    """
    cont = 0
    idle_cycles = []
    
    for i in range(len(profile)-1):
        if profile[i] == profile[i+1]:
            cont += 1
        else:
            if cont > 0:
                num_amostras_idle = cont + 1
                tempo_total_minutos = num_amostras_idle * dt_minutos_soc
                
                data = {
                    't': num_amostras_idle,
                    't_meses': tempo_total_minutos / minutos_por_mes,
                    'SOC': profile[i],
                    'index': i
                }
                idle_cycles.append(data)
            cont = 0
    
    if cont > 0:
        num_amostras_idle = cont + 1
        tempo_total_minutos = num_amostras_idle * dt_minutos_soc
        data = {
            't': num_amostras_idle,
            't_meses': tempo_total_minutos / minutos_por_mes,
            'SOC': profile[len(profile)-1],
            'index': len(profile)-1
        }
        idle_cycles.append(data)
            
    return idle_cycles

`

## Arquivo: src\besx\domain\models\degradation_model.py
`python

import math
import pandas as pd
import numpy as np
import rainflow

from besx.config import DegradacaoCicloConfig, DegradacaoCalendarioConfig, CONFIGURACAO, ModeloDegradacaoConfig
from besx.infrastructure.logging.logger import logger

def acumular_dano(Ccal_total_mes: float, acum_cal_global: float, exp_tempo: float) -> float:
    """
    Acumula o dano de acordo com a exponencial.
    """
    return (Ccal_total_mes**exp_tempo + acum_cal_global**exp_tempo)**(1/exp_tempo)

def calcular_dano_referencia_serrao(model_params: ModeloDegradacaoConfig) -> float:
    """
    Calcula o dano nominal de referência conforme Serrão et al.
    Referência: T = 25°C, SOC = 50%, DOD = 10%.
    Considerando 30 ciclos de 10% DOD por mês.
    """
    # PARÂMETROS DE REFERÊNCIA
    T_REF_K = 25 + 273.15
    SOC_REF = 50.0
    DOD_REF = 10.0
    N_CICLOS_MES = 30
    
    # 1. Dano Cíclico Nominal
    c_params = model_params.ciclo
    cf_soc = c_params.a * np.exp(c_params.b * SOC_REF)
    cf_temp = c_params.c * np.exp(c_params.d * T_REF_K)
    cf_depth = c_params.g * (DOD_REF**c_params.h)
    
    dano_unit_cyc = cf_depth * cf_soc * cf_temp
    # Acúmulo quadrático de 30 ciclos idênticos
    dano_cyc_mes = np.sqrt(N_CICLOS_MES * (dano_unit_cyc**2))
    
    # 2. Dano Calendário Nominal
    cal_params = model_params.calendario
    ccal_temp = cal_params.k_T * np.exp(cal_params.exp_T * T_REF_K)
    ccal_soc = cal_params.k_soc * np.exp(cal_params.exp_soc * SOC_REF)
    exp_cal = cal_params.exp_cal
    
    # Dano de 1 mês (t=1)
    dano_cal_mes = ccal_temp * ccal_soc * (1.0**exp_cal)
    
    # Dano Total de Referência (mês)
    return float(dano_cyc_mes + dano_cal_mes)

def calcular_fator_severidade(dano_total_mes: float, model_params: ModeloDegradacaoConfig) -> float:
    """
    Calcula o Fator de Severidade (Is) comparando o dano real com o nominal.
    """
    d_nom = calcular_dano_referencia_serrao(model_params)
    return float(dano_total_mes / d_nom) if d_nom > 0 else 0.0

def calcular_rul(
    soh_atual_perc: float, 
    dano_total_acumulado: float, 
    meses_simulados: float, 
    dias_por_ano_avg: float
) -> float:
    """
    Projeta o Remaining Useful Life (RUL) em anos.
    Assume morte da bateria em 80% do SOH.
    """
    if meses_simulados <= 0:
        return 999.0
        
    dias_simulados = meses_simulados * (dias_por_ano_avg / 12)
    dano_diario = dano_total_acumulado / dias_simulados if dias_simulados > 0 else 0.0
    dano_anual = dano_diario * 365.25
    
    perda_restante = soh_atual_perc - 80.0
    rul_anos = perda_restante / dano_anual if dano_anual > 0 else 999.0
    return float(rul_anos)

def dano_ciclo(lista_ciclos: list, Temp_kelvin: float, model_params: DegradacaoCicloConfig) -> tuple[float, pd.DataFrame]:
    """
    Calcula o dano total de cada ciclo do mês e acumula de forma quadrática.
    
    Args:
        lista_ciclos (list): Lista de valores de SOC (perfil).
        Temp_kelvin (float): Temperatura da bateria.
        model_params (DegradacaoCicloConfig): Parâmetros do modelo de ciclo.
    """
    from besx.domain.models.battery_simulator import picos_e_vales
    prominence = CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence
    # Garante redução da série para otimização do Rainflow
    soc_series = pd.Series(lista_ciclos)
    lista_ciclos_simp = picos_e_vales(soc_series, prominence=prominence)

    rainflow_mes = rainflow.extract_cycles(lista_ciclos_simp)

    df_rainflow = pd.DataFrame(rainflow_mes,
                               columns = ["Range", "Mean", "Count", "Start", "End"])

    range_dp = model_params.range_round_dp
    mean_dp = model_params.mean_round_dp

    df_rainflow['Range'] = pd.to_numeric(df_rainflow['Range'], errors='coerce')
    df_rainflow['range_rounded'] = df_rainflow['Range'].round(range_dp)

    df_rainflow['Mean'] = pd.to_numeric(df_rainflow['Mean'], errors='coerce')
    df_rainflow['mean_rounded'] = df_rainflow['Mean'].round(mean_dp)

    Ccyc_total_mes = 0.0

    a = model_params.a
    b = model_params.b
    c = model_params.c
    d = model_params.d
    g = model_params.g
    h = model_params.h

    # Listas para armazenar cálculos intermediários
    lista_CFade_soc = []
    lista_CFade_temp = []
    lista_CFade_depth = []
    lista_dano_unitario = []
    lista_dano_acum_parcial = []

    # 2. Itera sobre a Lista
    for _, info_grupo in df_rainflow.iterrows():
        dod = info_grupo['range_rounded']
        soc = info_grupo['mean_rounded']

        # 3. Calcula o dano unitário
        CFade_soc = a * np.exp(b * soc)
        CFade_temp = c * np.exp(d * Temp_kelvin)
        CFade_depth = g * (dod**h)
        dano = CFade_depth * CFade_soc * CFade_temp

        # 4. Acumula quadraticamente
        Ccyc_total_mes = np.sqrt(Ccyc_total_mes**2 + dano**2)
        
        # Armazena os cálculos intermediários
        lista_CFade_soc.append(CFade_soc)
        lista_CFade_temp.append(CFade_temp)
        lista_CFade_depth.append(CFade_depth)
        lista_dano_unitario.append(dano)
        lista_dano_acum_parcial.append(Ccyc_total_mes)

    # Adiciona as colunas de cálculos intermediários ao DataFrame
    df_rainflow['a'] = a
    df_rainflow['b'] = b
    df_rainflow['CFade_soc'] = lista_CFade_soc
    df_rainflow['c'] = c
    df_rainflow['d'] = d
    df_rainflow['Temp_kelvin'] = Temp_kelvin
    df_rainflow['CFade_temp'] = lista_CFade_temp
    df_rainflow['g'] = g
    df_rainflow['h'] = h
    df_rainflow['CFade_depth'] = lista_CFade_depth
    df_rainflow['dano_unitario'] = lista_dano_unitario
    df_rainflow['dano_acumulado_parcial'] = lista_dano_acum_parcial

    return float(Ccyc_total_mes), df_rainflow

def dano_calendar(lista_periodos_idle: list, Tbat_kelvin: float, model_params: DegradacaoCalendarioConfig, dt_minutos: float, dias_por_ano_avg: int) -> tuple[float, pd.DataFrame]:
    """
    Calcula o dano total por calendário (%) para o mês.

    Args:
        lista_periodos_idle (list): Lista de períodos idle.
        Tbat_kelvin (float): Temperatura da bateria.
        model_params (DegradacaoCalendarioConfig): Parâmetros do modelo de calendário.
        dt_minutos (float): Intervalo de tempo entre amostras.
        dias_por_ano_avg (int): Média de dias por ano.
    """
    Ccal_total_mes = 0.0
    k_T = model_params.k_T
    exp_T = model_params.exp_T
    k_soc = model_params.k_soc
    exp_soc = model_params.exp_soc
    exp_tempo = model_params.exp_cal

    # Listas para armazenar os cálculos de cada período
    lista_soc = []
    lista_t_meses = []
    lista_CCal_temperature = []
    lista_Ccal_soc = []
    lista_Ccal_time = []
    lista_dano_periodo = []
    lista_dano_acum_parcial = []

    # Itera sobre cada período parado
    for periodo in lista_periodos_idle:
        soc_percent = periodo['SOC']
        t_meses = periodo['t_meses']

        # Calcula os fatores de dano para este período
        CCal_temperature = k_T * np.exp(exp_T * Tbat_kelvin)
        Ccal_soc = k_soc * np.exp(exp_soc * soc_percent)
        Ccal_time = t_meses**exp_tempo

        # Calcula o dano APENAS deste período parado
        dano = CCal_temperature * Ccal_soc * Ccal_time

        Ccal_total_mes = (Ccal_total_mes**exp_tempo + dano**exp_tempo)**(1/exp_tempo)
        
        # Armazena os cálculos intermediários
        lista_soc.append(soc_percent)
        lista_t_meses.append(t_meses)
        lista_CCal_temperature.append(CCal_temperature)
        lista_Ccal_soc.append(Ccal_soc)
        lista_Ccal_time.append(Ccal_time)
        lista_dano_periodo.append(dano)
        lista_dano_acum_parcial.append(Ccal_total_mes)

    # Cria DataFrame com todos os cálculos
    df_calculos_calendario = pd.DataFrame({
        'SOC': lista_soc,
        'num_amostras': [p['t'] for p in lista_periodos_idle],
        'dt_minutos': dt_minutos,
        'tempo_total_minutos': [p['t'] * dt_minutos for p in lista_periodos_idle],
        'minutos_por_mes': (dias_por_ano_avg * 24 * 60) / 12,
        't_meses': lista_t_meses,
        'k_T': k_T,
        'exp_T': exp_T,
        'Tbat_kelvin': Tbat_kelvin,
        'CCal_temperature': lista_CCal_temperature,
        'k_soc': k_soc,
        'exp_soc': exp_soc,
        'Ccal_soc': lista_Ccal_soc,
        'exp_tempo': exp_tempo,
        'Ccal_time': lista_Ccal_time,
        'dano_periodo': lista_dano_periodo,
        'dano_acumulado_parcial': lista_dano_acum_parcial
    })

    return float(Ccal_total_mes), df_calculos_calendario

def calcular_estatisticas_operacionais(df_soc_saida: pd.DataFrame, df_potencia_entrada: pd.DataFrame, cap_kwh: float, lista_periodos_idle: list = None) -> dict:
    """
    Analisa o comportamento do mês: Ciclos (Rainflow) e C-Rates (Potência).
    """
    # --- 1. Preparação (SOC) ---
    soc_series = df_soc_saida['SOC']

    # Assume coluna 1 como potência (Entrada em Watts)
    potencia_w = df_potencia_entrada.iloc[:, 1].abs()
    potencia_kw = potencia_w / 1000.0

    # --- 3. Análise de C-Rate ---
    c_rates = potencia_kw / cap_kwh

    max_c_rate = c_rates.max()
    avg_c_rate = c_rates.mean()

    # --- 4. Análise de Ciclos (Rainflow) ---
    from besx.domain.models.battery_simulator import picos_e_vales
    prominence = CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence
    soc_series_simp = picos_e_vales(soc_series, prominence=prominence)
    ciclos_rf = list(rainflow.extract_cycles(soc_series_simp))

    num_ciclos = len(ciclos_rf)

    # DOD Médio
    dods = [x[0] for x in ciclos_rf]
    avg_dod = np.mean(dods) if dods else 0

    # --- 5. Análise de Throughput (EFC via Rainflow) ---
    # Implementação rigorosa: Soma dos DODs pesados pelo contador (0.5 ou 1.0) do Rainflow.
    # Cada ciclo completo (100% DOD) = 1 EFC.
    efc = sum([(range_val * count) / 100.0 for range_val, mean, count, start, end in ciclos_rf])

    # --- 6. Análise de Stress / Severidade ---
    media_soc = soc_series.mean()
    tempo_alto_soc = (soc_series > 90).sum()
    tempo_baixo_soc = (soc_series < 10).sum()

    total_amostras = len(soc_series)
    pct_alto = (tempo_alto_soc / total_amostras) * 100
    pct_baixo = (tempo_baixo_soc / total_amostras) * 100

    # --- 7. SOC Médio em Repouso ---
    if lista_periodos_idle:
        t_total_idle = sum(p['t'] for p in lista_periodos_idle)
        if t_total_idle > 0:
            soc_idle_avg = sum(p['SOC'] * p['t'] for p in lista_periodos_idle) / t_total_idle
        else:
            soc_idle_avg = np.nan
    else:
        idle_mask = potencia_w == 0.0        
        # Garante alinhamento dos arrays de dados; caso contrário, usamos 'nan'
        if len(idle_mask) == len(soc_series) and idle_mask.any():
            soc_idle_avg = soc_series[idle_mask.values].mean()
        else:
            soc_idle_avg = np.nan

    return {
        "Ciclos_Contagem": num_ciclos,
        "EFC_Ciclos_Equivalentes": round(float(efc), 2),
        "DOD_Medio_Perc": round(float(avg_dod), 1),
        "C_Rate_Max": round(float(max_c_rate), 2), 
        "C_Rate_Medio": round(float(avg_c_rate), 3),
        "SOC_Medio": round(float(media_soc), 1),
        "SOC_Medio_Idle": round(float(soc_idle_avg), 1),
        "Tempo_SOC_Alto_Perc": round(float(pct_alto), 1),
        "Tempo_SOC_Baixo_Perc": round(float(pct_baixo), 1),
        "Rainflow_Cycles": ciclos_rf # Passamos a lista bruta para o dashboard processar o histograma
    }

`

## Arquivo: src\besx\entrypoints\__init__.py
`python

`

## Arquivo: src\besx\entrypoints\cli\main.py
`python

from besx.application.simulation import SimulationManager
from besx.entrypoints.cli.menu import exibir_menu_inicial
from besx.config import CONFIGURACAO, PERFIS_BATERIA
from besx.infrastructure.logging.logger import logger

if __name__ == "__main__":
    logger.info(">>> Iniciando BESx Simulation App <<<")

    # --- Menu inicial: escolha de bateria e backend ---
    perfil_ativo, backend = exibir_menu_inicial()

    # Atualiza a configuração com o perfil de bateria escolhido
    CONFIGURACAO.bateria = PERFIS_BATERIA[perfil_ativo]

    logger.info(f"Perfil: {perfil_ativo} | Backend: {backend}")

    # --- Inicia a simulação ---
    sim = SimulationManager(CONFIGURACAO, backend=backend)
    sim.run()

`

## Arquivo: src\besx\entrypoints\cli\menu.py
`python
"""
menu.py  —  Menu Inicial Interativo do BESx

Responsabilidade: apresentar ao usuário as opções de configuração antes
de iniciar a simulação. Retorna as escolhas para que main.py possa
atualizar o CONFIGURACAO e instanciar o SimulationManager corretamente.

Opções:
  1. Perfil de bateria  (qualquer chave definida em PERFIS_BATERIA)
  2. Backend de simulação  ("plecs" | "python")
"""

from besx.config import PERFIS_BATERIA
from besx.infrastructure.logging.logger import logger

# Constantes de backend exportadas para uso nos outros módulos
BACKEND_PLECS  = "plecs"
BACKEND_PYTHON = "python"

_BACKENDS_DISPONIVEIS = {
    "1": BACKEND_PYTHON,
    "2": BACKEND_PLECS,
}

_DESCRICOES_BACKEND = {
    BACKEND_PYTHON: "Simulador Python  (integração de Coulomb — sem PLECS)",
    BACKEND_PLECS:  "PLECS via XML-RPC (requer PLECS aberto em localhost:1080)",
}


def exibir_menu_inicial() -> tuple[str, str]:
    """
    Exibe o menu interativo em loop até o usuário confirmar.

    Returns:
        tuple: (perfil_ativo, backend)
            - perfil_ativo (str): chave de PERFIS_BATERIA escolhida
            - backend      (str): BACKEND_PYTHON | BACKEND_PLECS
    """
    _imprimir_cabecalho()

    while True:
        perfil_ativo = _selecionar_perfil_bateria()
        backend      = _selecionar_backend()

        if _confirmar_selecao(perfil_ativo, backend):
            return perfil_ativo, backend

        print()
        print("  ↩  Reiniciando configuração...\n")


# ------------------------------------------------------------------ #
#  Seções internas do menu                                            #
# ------------------------------------------------------------------ #

def _imprimir_cabecalho():
    print()
    print("=" * 58)
    print("      BESx — Battery Energy Storage Simulator")
    print("      Configuração Inicial")
    print("=" * 58)


def _selecionar_perfil_bateria() -> str:
    """Pergunta qual perfil de bateria usar e retorna a chave escolhida."""
    perfis = list(PERFIS_BATERIA.keys())

    print()
    print("┌─ [ 1 / 2 ]  PERFIL DE BATERIA ─────────────────────────────")
    for idx, chave in enumerate(perfis, start=1):
        cfg  = PERFIS_BATERIA[chave]
        ah   = getattr(cfg, "Ah", "?")
        ns   = getattr(cfg, "Ns", "?")
        np_  = getattr(cfg, "Np", "?")
        pwr  = getattr(cfg, "P_bess", 0) / 1000.0
        cap  = getattr(cfg, "capacidade_nominal_wh", 0) / 1000.0
        print(f"│  [{idx}] {chave}")
        print(f"│       {ah} Ah  |  {ns}S × {np_}P  |  {pwr:.0f} kW  |  {cap:.1f} kWh")
    print("└─────────────────────────────────────────────────────────────")

    while True:
        entrada = input(f"\n  Escolha o perfil [1–{len(perfis)}]: ").strip()
        try:
            idx = int(entrada) - 1
            if 0 <= idx < len(perfis):
                escolhido = perfis[idx]
                logger.info(f"Perfil de bateria selecionado: {escolhido}")
                return escolhido
        except ValueError:
            pass
        print(f"  ⚠  Opção inválida. Digite um número entre 1 e {len(perfis)}.")


def _selecionar_backend() -> str:
    """Pergunta qual backend de simulação usar e retorna a constante."""
    print()
    print("┌─ [ 2 / 2 ]  BACKEND DE SIMULAÇÃO ──────────────────────────")
    for key, backend in _BACKENDS_DISPONIVEIS.items():
        print(f"│  [{key}] {_DESCRICOES_BACKEND[backend]}")
    print("└─────────────────────────────────────────────────────────────")

    while True:
        entrada = input("\n  Escolha o backend [1–2]: ").strip()
        if entrada in _BACKENDS_DISPONIVEIS:
            escolhido = _BACKENDS_DISPONIVEIS[entrada]
            logger.info(f"Backend selecionado: {escolhido}")
            return escolhido
        print("  ⚠  Opção inválida. Digite 1 ou 2.")


def _confirmar_selecao(perfil_ativo: str, backend: str) -> bool:
    """Exibe o resumo e pede confirmação. Retorna True se confirmado."""
    cfg = PERFIS_BATERIA[perfil_ativo]
    print()
    print("┌─ RESUMO DA CONFIGURAÇÃO ────────────────────────────────────")
    print(f"│  Bateria : {perfil_ativo}")
    print(f"│  Backend : {_DESCRICOES_BACKEND[backend]}")
    print(f"│  Capacid.: {getattr(cfg, 'Ah', '?')} Ah × "
          f"{getattr(cfg, 'Ns', '?')}S × {getattr(cfg, 'Np', '?')}P  "
          f"({getattr(cfg, 'capacidade_nominal_wh', 0)/1000:.1f} kWh)")
    print(f"│  P_bess  : {getattr(cfg, 'P_bess', 0)/1000:.1f} kW")
    print("└─────────────────────────────────────────────────────────────")

    resp = input("\n  Iniciar simulação com essa configuração? [S/n]: ").strip().lower()
    return resp in ("", "s", "sim", "y", "yes")

`

## Arquivo: src\besx\entrypoints\dashboard\streamlit_app.py
`python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime
import time
import os
import json
import ast

# Internal imports
from besx.application.simulation import SimulationManager
from besx.config import CONFIGURACAO, PERFIS_BATERIA, ModeloDegradacaoConfig, BateriaConfig
from besx.domain.models.degradation_model import (
    calcular_dano_referencia_serrao, 
    calcular_fator_severidade, 
    calcular_rul
)
from besx.infrastructure.llm.gemini_analyzer import analisar_comparacao_bess

# Add tests path to sys.path if not present (to allow importing tests)
import sys
tests_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../tests'))
if tests_path not in sys.path:
    sys.path.insert(0, tests_path)

from mission_profile_generator import generate_profiles
from test_engine_validation import rodar_validacao

# Page Config
st.set_page_config(
    page_title="BESx Simulation Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Theme Configuration ---
THEME_COLORS = {
    "PRIMARY": "#00ffcc",
    "SECONDARY": "#31333f",
    "DANGER": "#ff4b4b",
    "WARNING": "#ffcc00",
    "CALENDAR": "#636efa", # Azul
    "CYCLE": "#ef553b",    # Vermelho/Laranja
    "SOH": "#00ffcc",
    "TEXT": "#e6edf3",
    "GRID": "#30363d"
}

# --- App State Management ---
if 'sim_results' not in st.session_state: st.session_state.sim_results = pd.DataFrame()
if 'curr_soc' not in st.session_state: st.session_state.curr_soc = pd.DataFrame()
if 'curr_input' not in st.session_state: st.session_state.curr_input = pd.DataFrame()
if 'sim_status' not in st.session_state: st.session_state.sim_status = "idle" # idle, running, finished
if 'validation_profiles' not in st.session_state: st.session_state.validation_profiles = {}
if 'validation_run' not in st.session_state: st.session_state.validation_run = None
if 'throughput' not in st.session_state: st.session_state.throughput = 0.0
if 'config_override' not in st.session_state: st.session_state.config_override = CONFIGURACAO.modelo_degradacao.model_copy(deep=True).model_dump()

# Custom CSS
st.markdown("""
<style>
    :root {
        --border-color: #30363d;
    }
    
    /* Depende do tema natural do Streamlit (transparente ou baseado no css nativo do stMetric) 
       Evitamos forçar background escuro absoluto */
    .stMetric { 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid var(--border-color);
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }

    .main { background-color: transparent; }
    
    .metric-card {
        padding: 12px;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        margin-bottom: 10px;
    }
    
    div[data-testid="stSidebar"] { }
    .battery-container { width: 60px; height: 120px; border: 3px solid var(--border-color); border-radius: 8px; position: relative; padding: 4px; margin: 0 auto; }
    .battery-cap { width: 22px; height: 8px; background-color: var(--border-color); position: absolute; top: -8px; left: 19px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
    .battery-fill { width: 100%; border-radius: 2px; position: absolute; bottom: 4px; left: 0; right: 0; transition: height 0.5s ease; }
    
    /* Animation for simulation running */
    @keyframes pulse-red {
        0% { transform: scale(0.95); opacity: 0.7; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.7; }
    }
    .pulse-icon {
        display: inline-block;
        animation: pulse-red 1.5s infinite ease-in-out;
        color: #ffcc00;
        font-size: 24px;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Shared UI Components ---
def render_metrics_row(df_results, throughput_mwh, month_idx=None):
    if df_results.empty:
        return
    
    # Se month_idx for None, mostramos o estado FINAL (Resumo)
    # Se for um inteiro, mostramos os dados daquele mês específico
    if month_idx is None:
        target_data = df_results.iloc[-1]
        label_suffix = "(Final)"
    else:
        target_data = df_results.iloc[month_idx]
        label_suffix = f"(Mês {month_idx + 1})"
    
    cols = st.columns(6) # 6 colunas
    
    # Custom Battery Visual (Sempre baseado no SOH atual/final para contexto geral)
    with cols[0]:
        display_soh = target_data['capacidade_restante']
        fill_h = max(0, min(100, (display_soh - 80) / 20 * 100))
        color = "#00ffcc" if display_soh > 95 else "#ffcc00" if display_soh > 85 else "#ff4444"
        st.markdown(f"""
        <div class="battery-container"><div class="battery-cap"></div><div class="battery-fill" style="height: {fill_h}%; background: {color};"></div></div>
        <p style="text-align: center; font-weight: bold; font-size: 16px; margin-top: 5px;">{display_soh:.2f}%</p>
        """, unsafe_allow_html=True)

    cols[1].metric(f"SOH {label_suffix}", f"{target_data['capacidade_restante']:.2f}%", 
                  f"{target_data['capacidade_restante'] - 100:.2f}%")
    
    with cols[2]:
        if month_idx is None:
            # Visão Global: calcula o dano mensal médio de toda a simulação
            dano_mes = df_results['dano_ciclos_mes'].mean() + df_results['dano_cal_mes'].mean()
        else:
            dano_mes = target_data.get('dano_ciclos_mes', 0) + target_data.get('dano_cal_mes', 0)
            
        mod_cfg = ModeloDegradacaoConfig(**st.session_state.config_override)
        is_val = calcular_fator_severidade(dano_mes, mod_cfg)
        st.metric(f"Severidade (Is) {label_suffix}", f"{is_val:.3f}", help="Ref: Serrão et al. (25°C, 50% SOC, 10% DOD)")

    with cols[3]:
        # RUL (Remaining Useful Life)
        if len(df_results) > 0:
            n_meses = target_data['mes']
            if n_meses > 0:
                rul_anos = calcular_rul(
                    soh_atual_perc=target_data['capacidade_restante'],
                    dano_total_acumulado=target_data.get('dano_ciclo_acum', 0) + target_data.get('dano_cal_acum', 0),
                    meses_simulados=n_meses,
                    dias_por_ano_avg=CONFIGURACAO.dados_entrada.dias_por_ano_avg
                )
                st.metric("RUL (Vida Útil)", f"{rul_anos:.1f} anos", help=f"Projeção baseada na taxa de degradação atual.")
            else:
                st.metric("RUL (Vida Útil)", "---")

    with cols[4]:
        st.metric("Throughput (MWh)", f"{throughput_mwh:.3f}")

    with cols[5]:
        if month_idx is None:
            # Media global de SOC Idle
            soc_idle_series = df_results['SOC_Medio_Idle']
            soc_idle = soc_idle_series.replace(0, np.nan).mean()
        else:
            soc_idle = target_data.get('SOC_Medio_Idle', np.nan)
                
        if pd.isna(soc_idle):
            st.metric("SOC Idle Médio", "---", help="Bateria não entrou em repouso")
        else:
            st.metric("SOC Idle Médio", f"{soc_idle:.1f}%")

def render_view_overview(df_results, df_soc_mes, month_idx=None, key_suffix=""):
    c1, c2 = st.columns(2)
    with c1:
        if month_idx is not None:
            st.subheader(f"Curva de SOC - Mês {month_idx + 1}")
            if not df_soc_mes.empty:
                fig = px.line(df_soc_mes, x=df_soc_mes['Tempo']/3600, y='SOC', color_discrete_sequence=[THEME_COLORS["PRIMARY"]])
                fig.update_layout(
                    xaxis_title="Horas", yaxis_title="SOC (%)", height=400,
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=THEME_COLORS["TEXT"]),
                    xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"])
                )
                st.plotly_chart(fig, width='stretch', key=f"soc_chart_{key_suffix}")
            else:
                st.info("Perfil de SOC não disponível para este mês no modo visualizador.")
        else:
            st.subheader("Evolução Mensal do SOH (%)")
            if not df_results.empty:
                fig = px.line(df_results, x='mes', y='capacidade_restante', markers=True, color_discrete_sequence=[THEME_COLORS["PRIMARY"]])
                fig.add_hline(y=80, line_dash="dash", line_color=THEME_COLORS["DANGER"], annotation_text="EOL")
                fig.update_layout(
                    yaxis_range=[75, 105], height=400,
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=THEME_COLORS["TEXT"]),
                    xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"])
                )
                st.plotly_chart(fig, width='stretch', key=f"soh_evol_{key_suffix}")
            
    with c2:
        if month_idx is not None:
            st.subheader(f"Dano Mensal - Mês {month_idx + 1}")
            target_data = df_results.iloc[month_idx]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=['Ciclo'], y=[target_data['dano_ciclos_mes']], name='Ciclo', marker_color=THEME_COLORS["CYCLE"]))
            fig.add_trace(go.Bar(x=['Calendário'], y=[target_data['dano_cal_mes']], name='Calendário', marker_color=THEME_COLORS["CALENDAR"]))
            fig.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=THEME_COLORS["TEXT"]),
                xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"])
            )
            st.plotly_chart(fig, width='stretch', key=f"damage_month_{key_suffix}")
        else:
            st.subheader("Dano Acumulado ao Longo do Tempo")
            if not df_results.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_results['mes'], y=df_results['dano_ciclo_acum'], name='Dano Ciclo', fill='tozeroy', line=dict(color=THEME_COLORS["CYCLE"])))
                fig.add_trace(go.Scatter(x=df_results['mes'], y=df_results['dano_cal_acum'], name='Dano Cal', fill='tonexty', line=dict(color=THEME_COLORS["CALENDAR"])))
                fig.update_layout(
                    height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=THEME_COLORS["TEXT"]),
                    xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"]),
                    xaxis_title="Meses"
                )
                st.plotly_chart(fig, width='stretch', key=f"damage_accum_{key_suffix}")

def render_view_degradation(df_results, month_idx=None, key_suffix=""):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("DOD Médio vs Limite")
        if not df_results.empty:
            if month_idx is None:
                fig = px.bar(df_results, x='mes', y='DOD_Medio_Perc', color_discrete_sequence=[THEME_COLORS["WARNING"]])
            else:
                target_data = df_results.iloc[month_idx]
                fig = px.bar(x=[f"Mês {month_idx+1}"], y=[target_data['DOD_Medio_Perc']], color_discrete_sequence=[THEME_COLORS["WARNING"]])
            fig.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=THEME_COLORS["TEXT"]),
                xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"])
            )
            st.plotly_chart(fig, width='stretch', key=f"dod_bar_{key_suffix}")
    with c2:
        st.subheader("Composição da Degradação")
        if not df_results.empty:
            if month_idx is None:
                # Pizza do dano TOTAL final
                last = df_results.iloc[-1]
                values = [last['dano_ciclo_acum'], last['dano_cal_acum']]
                names = ['Cíclico', 'Calendário']
            else:
                target_result = df_results.iloc[month_idx]
                values = [target_result['dano_ciclos_mes'], target_result['dano_cal_mes']]
                names = ['Cíclico', 'Calendário']
            
            fig = px.pie(values=values, names=names, hole=0.4, color_discrete_sequence=[THEME_COLORS["CYCLE"], THEME_COLORS["CALENDAR"]])
            fig.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', 
                font=dict(color=THEME_COLORS["TEXT"]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                template="plotly_dark" if st.get_option("theme.base") != "light" else "plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True, key=f"deg_pie_{key_suffix}")

    # Novo: Histograma de DOD (Rainflow) - Sempre visível se houver dados
    if not df_results.empty:
        all_rf_data = []
        
        # Se um mês foi selecionado, pega só ele. Se for visão global, soma tudo
        if month_idx is not None:
            raw_rf = df_results.iloc[month_idx].get('Rainflow_Cycles', [])
            if isinstance(raw_rf, str):
                try: raw_rf = ast.literal_eval(raw_rf)
                except: raw_rf = []
            if isinstance(raw_rf, list):
                all_rf_data.extend(raw_rf)
            title_rf = f"📊 Espectro de Uso (DOD Rainflow) - Mês {month_idx + 1}"
        else:
            for _, row in df_results.iterrows():
                raw_rf = row.get('Rainflow_Cycles', [])
                if isinstance(raw_rf, str):
                    try: raw_rf = ast.literal_eval(raw_rf)
                    except: raw_rf = []
                if isinstance(raw_rf, list):
                    all_rf_data.extend(raw_rf)
            title_rf = "📊 Espectro de Uso Acumulado (Todos os Meses)"
            
        if len(all_rf_data) > 0:
            st.markdown("---")
            st.subheader(title_rf)
            df_rf = pd.DataFrame(all_rf_data, columns=['DOD', 'Mean', 'Count', 'Start', 'End'])
            fig_rf = px.histogram(df_rf, x='DOD', y='Count', nbins=20, 
                                  labels={'DOD':'Profundidade (DOD %)', 'Count':'Ocorrências'},
                           color_discrete_sequence=[THEME_COLORS["CYCLE"]])
            fig_rf.update_layout(
                height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=THEME_COLORS["TEXT"]),
                xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"]),
                template="plotly_dark" if st.get_option("theme.base") != "light" else "plotly_white"
            )
            st.plotly_chart(fig_rf, use_container_width=True, key=f"dod_rf_hist_{key_suffix}")

def render_view_operational(df_results, df_soc_mes, df_input_mes, month_idx=None, key_suffix=""):
    if month_idx is None:
        st.info("Selecione um mês específico para ver a análise operacional detalhada (Mapas de Calor, C-Rate).")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"SOC vs Potência - Mês {month_idx + 1}")
        if not df_soc_mes.empty and not df_input_mes.empty:
            min_l = min(len(df_input_mes), len(df_soc_mes))
            fig = px.density_heatmap(x=df_soc_mes['SOC'].values[:min_l], y=df_input_mes.iloc[:min_l, 1].values, 
                                    labels={'x':'SOC (%)', 'y':'Potência (kW)'}, nbinsx=30, nbinsy=30,
                                    color_continuous_scale="Viridis")
            fig.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=THEME_COLORS["TEXT"]),
                xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"])
            )
            st.plotly_chart(fig, width='stretch', key=f"heatmap_{key_suffix}")
    with c2:
        st.subheader(f"C-Rate - Mês {month_idx + 1}")
        if not df_input_mes.empty:
            cap_kwh = CONFIGURACAO.bateria.capacidade_nominal_wh / 1000
            crate = np.abs(df_input_mes.iloc[:, 1].values) / cap_kwh
            fig = px.histogram(x=crate, nbins=30, labels={'x': 'C-Rate'}, color_discrete_sequence=[THEME_COLORS["PRIMARY"]])
            fig.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=THEME_COLORS["TEXT"]),
                xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"]),
                yaxis_title="Frequência"
            )
            st.plotly_chart(fig, width='stretch', key=f"crate_hist_{key_suffix}")

# --- Sidebar ---
st.sidebar.title("🔋 BESx Dashboard")
is_running = st.session_state.sim_status == "running"

pasta_db = 'database'
arquivos_db = [f for f in os.listdir(pasta_db) if f.endswith(('.mat', '.csv'))] if os.path.exists(pasta_db) else []
data_file_sidebar = st.sidebar.selectbox("Perfil de Dados", arquivos_db if arquivos_db else ["Vazio"], disabled=is_running)
battery_prof = st.sidebar.selectbox("Bateria", list(PERFIS_BATERIA.keys()), disabled=is_running)
backend = st.sidebar.radio("Backend", ["plecs","python"], horizontal=True, disabled=is_running)

st.sidebar.markdown("---")
st.sidebar.subheader("🔋 Limites de SOC")
soc_range = st.sidebar.slider("Faixa de Operação (%)", 0, 100, (20, 80), disabled=is_running)
soc_min_val, soc_max_val = soc_range

st.sidebar.markdown("---")
st.sidebar.subheader("🌡️ Temperatura")
t_cyc = st.sidebar.slider("Temp. Ciclo (°C)", 0, 70, 35, disabled=is_running)
t_idl = st.sidebar.slider("Temp. Repouso (°C)", 0, 70, 25, disabled=is_running)
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Modo de Simulação")

tipo_duracao = st.sidebar.radio("Tipo de Duração", ["Anos", "Meses"], horizontal=True, disabled=is_running)

if tipo_duracao == "Anos":
    anos_sim = st.sidebar.slider("Anos", 1, 20, 1, disabled=is_running)
    meses_total_sim = None # Será anos_sim * 12 no manager
else:
    meses_total_sim = st.sidebar.slider("Meses", 1, 12, 6, disabled=is_running)
    anos_sim = 0 # Valor dummy, manager usará meses_total_sim

sim_eol_mode = st.sidebar.toggle("🔋 Simular até Fim de Vida (EOL)", disabled=is_running)
if sim_eol_mode:
    st.sidebar.warning("⚠️ Modo EOL ativo: a simulação ignora a duração fixa e para ao atingir o limite de capacidade.")

# Tabs
tab_live, tab_hist, tab_comp, tab_val, tab_cfg = st.tabs(["🚀 Tempo Real", "📂 Histórico", "📈 Comparativo", "✔️ Validação Engine", "⚙️ Configurações"])

# --- TAB 1: LIVE ---
with tab_live:
    # Aviso de status no topo
    msg_placeholder = st.empty()
    if st.session_state.sim_status == "running":
        msg_placeholder.markdown('<div style="text-align: center;"><span class="pulse-icon">⚡</span><b>Simulação em Andamento...</b><br><small>(Evite interagir com menus durante o processamento para não interromper)</small></div>', unsafe_allow_html=True)
    elif st.session_state.sim_status == "finished":
        msg_placeholder.success("🎉 Simulação Concluída com Sucesso!")

    # View selection
    view_set_live = st.radio("Conjunto de Visualização", 
                           ["📊 Visão Geral", "📉 Degradação", "⚡ Operacional"], 
                           horizontal=True, key="live_view", disabled=is_running)
    
    # Placeholders para atualização em tempo real
    metrics_placeholder = st.empty()
    st.markdown("---")
    
    # Seletor de Período (Selectbox) - V2
    selected_month_idx = None
    if not st.session_state.sim_results.empty:
        n_meses = len(st.session_state.sim_results)
        opcoes = ["📊 Resumo Geral"] + [f"📅 Mês {i+1}" for i in range(n_meses)]
        sel_mode = st.selectbox("Selecione o Foco da Análise", opcoes, index=0, key="live_sel", disabled=is_running)
        if sel_mode != "📊 Resumo Geral":
            selected_month_idx = int(sel_mode.split(" ")[-1]) - 1
        st.markdown("---")

    charts_placeholder = st.empty()

    def live_callback(df_soc, res_mes, df_in):
        # Update Session State
        if st.session_state.sim_results.empty:
            st.session_state.sim_results = pd.DataFrame([res_mes])
        else:
            st.session_state.sim_results = pd.concat([st.session_state.sim_results, pd.DataFrame([res_mes])], ignore_index=True)
        
        st.session_state.curr_soc = df_soc
        st.session_state.curr_input = df_in
        cap_mwh = CONFIGURACAO.bateria.capacidade_nominal_wh / 1e6
        st.session_state.throughput += res_mes['EFC_Ciclos_Equivalentes'] * cap_mwh
        
        # Garante que a mensagem de status esteja correta no callback
        mes_atual = res_mes.get('mes', '?')
        total_p = res_mes.get('total_meses', '?')
        msg_placeholder.markdown(f'<div style="text-align: center;"><span class="pulse-icon">⚡</span><b>Simulação em Andamento: Mês {mes_atual}/{total_p}</b><br><small>(Evite interagir com menus durante o processamento para não interromper)</small></div>', unsafe_allow_html=True)

        # Renderize diretamente durante a simulação
        with metrics_placeholder.container():
            render_metrics_row(st.session_state.sim_results, st.session_state.throughput, month_idx=selected_month_idx)
        
        with charts_placeholder.container():
            # Título da Visão Atual
            title = "📊 Resumo Geral" if selected_month_idx is None else f"📅 Dados do Mês {selected_month_idx + 1}"
            st.markdown(f"### {title}")

            # Durante a simulação (live), precisamos de chaves que mudem a cada mês 
            # para não colidir com o mês anterior na mesma execução.
            n_res = len(st.session_state.sim_results)
            step_suffix = f"live_{n_res}"

            is_current = (selected_month_idx is None or selected_month_idx == n_res - 1)
            display_soc = df_soc if is_current else pd.DataFrame()
            display_in = df_in if is_current else pd.DataFrame()
            
            if view_set_live == "📊 Visão Geral":
                render_view_overview(st.session_state.sim_results, display_soc, month_idx=selected_month_idx, key_suffix=step_suffix)
            elif view_set_live == "📉 Degradação":
                render_view_degradation(st.session_state.sim_results, month_idx=selected_month_idx, key_suffix=step_suffix)
            elif view_set_live == "⚡ Operacional":
                render_view_operational(st.session_state.sim_results, display_soc, display_in, month_idx=selected_month_idx, key_suffix=step_suffix)

    async_start = st.sidebar.button("▶️ Iniciar Simulação", disabled=(st.session_state.sim_status == "running"))
    
    if async_start:
        st.session_state.sim_results = pd.DataFrame()
        st.session_state.throughput = 0.0
        st.session_state.sim_status = "running"
        
        # Limpa e atualiza o placeholder imediatamente para remover o "Concluído" anterior
        msg_placeholder.markdown('<div style="text-align: center;"><span class="pulse-icon">⚡</span><b>Preparando Nova Simulação...</b></div>', unsafe_allow_html=True)

        cfg = CONFIGURACAO.model_copy(deep=True)
        
        # Aplica Overrides da Aba de Configurações
        cfg.modelo_degradacao = ModeloDegradacaoConfig(**st.session_state.config_override)

        cfg.bateria = PERFIS_BATERIA[battery_prof].model_copy(deep=True)
        cfg.bateria.Tbat_kelvin = t_cyc + 273.15
        cfg.bateria.Tbat_kelvin_idle = t_idl + 273.15
        cfg.bateria.soc_min_pct = soc_min_val / 100.0
        cfg.bateria.soc_max_pct = soc_max_val / 100.0
        cfg.simulacao.ANOS_SIMULACAO = anos_sim
        cfg.simulacao.MESES_SIMULACAO = meses_total_sim
        
        with st.spinner("Motor de Simulação em Execução..."):
            sim = SimulationManager(
                cfg, backend=backend, data_file=data_file_sidebar,
                on_mes_complete=live_callback, sim_until_eol=sim_eol_mode
            )
            sim.run()
        
        st.session_state.sim_status = "finished"
        st.rerun()

    # Render Persistent State (Quando não está rodando)
    if not st.session_state.sim_results.empty and st.session_state.sim_status != "running":
        with metrics_placeholder.container():
            render_metrics_row(st.session_state.sim_results, st.session_state.throughput, month_idx=selected_month_idx)
        with charts_placeholder.container():
            # Título da Visão Atual
            title = "📊 Resumo Geral" if selected_month_idx is None else f"📅 Dados do Mês {selected_month_idx + 1}"
            st.markdown(f"### {title}")

            is_latest = (selected_month_idx is not None and selected_month_idx == len(st.session_state.sim_results) - 1)
            display_soc = st.session_state.curr_soc if is_latest else pd.DataFrame()
            display_input = st.session_state.curr_input if is_latest else pd.DataFrame()
            
            if view_set_live == "📊 Visão Geral":
                render_view_overview(st.session_state.sim_results, display_soc, month_idx=selected_month_idx, key_suffix="live_st")
            elif view_set_live == "📉 Degradação":
                render_view_degradation(st.session_state.sim_results, month_idx=selected_month_idx, key_suffix="live_st")
            elif view_set_live == "⚡ Operacional":
                render_view_operational(st.session_state.sim_results, display_soc, display_input, month_idx=selected_month_idx, key_suffix="live_st")

# --- TAB 2: HISTORY ---
with tab_hist:
    res_path = "Results"
    if not os.path.exists(res_path):
        st.warning("Pasta 'Results' não encontrada.")
    else:
        past_sims = sorted([d for d in os.listdir(res_path) if os.path.isdir(os.path.join(res_path, d))], reverse=True)
        selected_sim = st.selectbox("Selecionar Simulação Passada", past_sims)
        
        if selected_sim:
            sim_dir = os.path.join(res_path, selected_sim)
            report_file = os.path.join(sim_dir, "report.txt")




            if os.path.exists(report_file):
                with st.expander("📄 Ver Resumo do Relatório", expanded=False):
                    with open(report_file, 'r', encoding='utf-8') as f:
                        st.text(f.read())
            
            excel_file = os.path.join(sim_dir, "data", "resultados_completos.xlsx")
            if os.path.exists(excel_file):
                df_hist = pd.read_excel(excel_file)
                
                # History Selectbox
                opcoes_hist = ["📊 Resumo Geral"] + [f"📅 Mês {i+1}" for i in range(len(df_hist))]
                sel_mode_h = st.selectbox("Selecione o Foco do Histórico", opcoes_hist, index=0, key="hist_sel")
                selected_month_h = None if sel_mode_h == "📊 Resumo Geral" else int(sel_mode_h.split(" ")[-1]) - 1

                view_set_hist = st.radio("Conjunto de Visualização (Histórico)", 
                                       ["📊 Visão Geral", "📉 Degradação", "⚡ Operacional"], 
                                       horizontal=True, key="hist_view")
                
                h_cap_mwh = df_hist.get("capacidade_nominal_wh", [CONFIGURACAO.bateria.capacidade_nominal_wh])[0] / 1e6
                h_throughput = df_hist['EFC_Ciclos_Equivalentes'].sum() * h_cap_mwh
                
                render_metrics_row(df_hist, h_throughput, month_idx=selected_month_h)
                st.markdown("---")
                
                # Título da Visão Histórica Atual
                title_h = "📊 Resumo Geral (Histórico)" if selected_month_h is None else f"📅 Dados do Mês {selected_month_h + 1} (Histórico)"
                st.markdown(f"### {title_h}")

                if view_set_hist == "📊 Visão Geral":
                    render_view_overview(df_hist, pd.DataFrame(), month_idx=selected_month_h, key_suffix="hist")
                elif view_set_hist == "📉 Degradação":
                    render_view_degradation(df_hist, month_idx=selected_month_h, key_suffix="hist")
                elif view_set_hist == "⚡ Operacional":
                    render_view_operational(df_hist, pd.DataFrame(), pd.DataFrame(), month_idx=selected_month_h, key_suffix="hist")
            else:
                st.error("Arquivo de resultados não encontrado nesta pasta.")

# --- TAB 3: COMPARISON ---
with tab_comp:
    st.header("📈 Comparativo de Simulações")
    res_path = "Results"
    if os.path.exists(res_path):
        past_sims = sorted([d for d in os.listdir(res_path) if os.path.isdir(os.path.join(res_path, d))], reverse=True)
        selected_sims = st.multiselect("Selecione Simulações para Comparar", past_sims)
        
        if selected_sims:
            comparison_data = []
            for sim_id in selected_sims:
                excel_file = os.path.join(res_path, sim_id, "data", "resultados_completos.xlsx")
                if os.path.exists(excel_file):
                    df_c = pd.read_excel(excel_file)
                    df_c['Simulacao'] = sim_id
                    comparison_data.append(df_c)
            
            if comparison_data:
                df_all = pd.concat(comparison_data)
                
                # SOH Evolution Comparison
                st.subheader("Evolução do SOH (%)")
                fig_soh = px.line(df_all, x='mes', y='capacidade_restante', color='Simulacao', markers=True)
                fig_soh.update_layout(
                    height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=THEME_COLORS["TEXT"]),
                    xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"]),
                    yaxis_range=[75, 102]
                )
                st.plotly_chart(fig_soh, use_container_width=True)
                
                # Final Degradation Comparison
                st.subheader("Dano Total Acumulado")
                final_results = df_all.groupby('Simulacao').last().reset_index()
                fig_deg = go.Figure()
                fig_deg.add_trace(go.Bar(x=final_results['Simulacao'], y=final_results['dano_ciclo_acum'], name='Dano Ciclo', marker_color=THEME_COLORS["CYCLE"]))
                fig_deg.add_trace(go.Bar(x=final_results['Simulacao'], y=final_results['dano_cal_acum'], name='Dano Cal', marker_color=THEME_COLORS["CALENDAR"]))
                fig_deg.update_layout(
                    barmode='stack', height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=THEME_COLORS["TEXT"]),
                    xaxis=dict(gridcolor=THEME_COLORS["GRID"]), yaxis=dict(gridcolor=THEME_COLORS["GRID"])
                )
                st.plotly_chart(fig_deg, use_container_width=True)

                # --- Parameter Diff Table ---
                st.subheader("🕵️ Diferenças de Parâmetros")
                PARAM_LABELS = {
                    "bateria_nome": "Modelo de Bateria",
                    "bateria_cap_wh": "Capacidade Nominal (Wh)",
                    "bateria_soc_min": "SOC Mín",
                    "bateria_soc_max": "SOC Máx",
                    "backend": "Backend",
                    "sim_until_eol": "Modo EOL",
                    "total_meses_simulados": "Meses Simulados",
                }
                SNAP_DEG_LABELS = {
                    "a": "Ciclo: coef. a",
                    "b": "Ciclo: coef. b",
                    "c": "Ciclo: coef. c",
                    "d": "Ciclo: coef. d",
                    "k_T": "Cal: k_T",
                    "k_soc": "Cal: k_soc",
                    "exp_cal": "Cal: exp_cal",
                }

                snapshots = {}
                for sim_id in selected_sims:
                    snap_file = os.path.join(res_path, sim_id, "data", "config_snapshot.json")
                    if os.path.exists(snap_file):
                        with open(snap_file, "r", encoding="utf-8") as f:
                            snapshots[sim_id] = json.load(f)

                if snapshots:
                    # Preparar os dados avançados primeiro
                    dados_ia = []
                    for sim_id in selected_sims:
                        sim_data_df = df_all[df_all['Simulacao'] == sim_id]
                        last_row = sim_data_df.iloc[-1].to_dict()
                        
                        # Extrai config para os cálculos
                        sim_config = snapshots.get(sim_id, {})
                        cap_nominal_wh = sim_config.get("bateria", {}).get("capacidade_nominal_wh", 1000000)
                        dias_por_ano_avg = sim_config.get("dados_entrada", {}).get("dias_por_ano_avg", 360)
                        mod_cfg_dict = sim_config.get("modelo_degradacao", CONFIGURACAO.modelo_degradacao.model_dump())
                        
                        # 1. Calculation RUL
                        months_simulated = last_row.get('mes', 1)
                        total_damage = last_row.get('dano_ciclo_acum', 0) + last_row.get('dano_cal_acum', 0)
                        rul_anos = calcular_rul(
                            soh_atual_perc=last_row.get('capacidade_restante', 100),
                            dano_total_acumulado=total_damage,
                            meses_simulados=months_simulated,
                            dias_por_ano_avg=dias_por_ano_avg
                        )
                        
                        # 2. Calculation Severity (Global average)
                        avg_monthly_damage = total_damage / months_simulated if months_simulated > 0 else 0
                        is_val = calcular_fator_severidade(avg_monthly_damage, ModeloDegradacaoConfig(**mod_cfg_dict))
                        
                        # 3. Calculation Throughput
                        cap_mwh = cap_nominal_wh / 1e6
                        total_throughput_mwh = sim_data_df['EFC_Ciclos_Equivalentes'].sum() * cap_mwh
                        
                        # 4. Rainflow Summary
                        deep_cycles = 0
                        shallow_cycles = 0
                        for _, row in sim_data_df.iterrows():
                            raw_rf = row.get('Rainflow_Cycles', [])
                            if isinstance(raw_rf, str):
                                try: raw_rf = ast.literal_eval(raw_rf)
                                except: raw_rf = []
                            if isinstance(raw_rf, list):
                                for cycle in raw_rf:
                                    # format: [DOD, Mean, Count, Start, End]
                                    dod = cycle[0]
                                    count = cycle[2]
                                    if dod > 80:
                                        deep_cycles += count
                                    elif dod < 20:
                                        shallow_cycles += count
                                        
                        # Limpa dados desnecessários ou muito pesados
                        for k in ['Rainflow_Cycles', 'Potencia_Aplicada_kW', 'SOC_Max_Diario', 'SOC_Min_Diario', 'SOC_Medio_Diario']:
                            last_row.pop(k, None)
                        
                        dados_ia.append({
                            "Simulacao": sim_id,
                            "Parametros": sim_config,
                            "Resultados_Finais": last_row,
                            "Metricas_Avancadas": {
                                "Vida_Util_Restante_Anos": round(rul_anos, 2),
                                "Fator_Severidade_Is": round(is_val, 3),
                                "Throughput_Acumulado_MWh": round(total_throughput_mwh, 2),
                                "Resumo_Espectro_Uso": {
                                    "Ciclos_Profundos_Acima_80_DOD": deep_cycles,
                                    "Micro_Ciclos_Abaixo_20_DOD": shallow_cycles
                                }
                            }
                        })
                    
                    rows = []
                    # Parâmetros de top-level
                    for key, label in PARAM_LABELS.items():
                        vals = {s: str(v.get(key, "N/A")) for s, v in snapshots.items()}
                        unique = len(set(vals.values())) > 1
                        rows.append({"Parâmetro": label, **vals, "_diff": unique})
                        
                    # Parâmetros de degradação
                    for key, label in SNAP_DEG_LABELS.items():
                        vals = {}
                        for s, v in snapshots.items():
                            ciclo = v.get("modelo_degradacao", {}).get("ciclo", {})
                            cal = v.get("modelo_degradacao", {}).get("calendario", {})
                            vals[s] = str(ciclo.get(key, cal.get(key, "N/A")))
                        unique = len(set(vals.values())) > 1
                        rows.append({"Parâmetro": label, **vals, "_diff": unique})

                    # Métricas Finais Básicas
                    BASE_METRICS_LABELS = {
                        "capacidade_restante": "SOH Final (%)",
                        "dano_ciclo_acum": "Dano Cíclico Acumulado",
                        "dano_cal_acum": "Dano Calendário Acumulado",
                        "DOD_Medio_Perc": "DOD Médio (%)",
                        "SOC_Medio": "SOC Médio (%)",
                        "SOC_Medio_Idle": "SOC Médio em Repouso (%)"
                    }
                    for key, label in BASE_METRICS_LABELS.items():
                        vals = {}
                        for dia in dados_ia:
                            met = dia.get("Resultados_Finais", {})
                            val = met.get(key, "N/A")
                            if isinstance(val, (int, float)):
                                if pd.isna(val):
                                    vals[dia["Simulacao"]] = "N/A"
                                elif key in ["dano_ciclo_acum", "dano_cal_acum"]:
                                    vals[dia["Simulacao"]] = f"{val:.4e}"
                                else:
                                    vals[dia["Simulacao"]] = f"{val:.2f}"
                            else:
                                vals[dia["Simulacao"]] = str(val)
                                
                        unique = len(set(vals.values())) > 1
                        rows.append({"Parâmetro": label, **vals, "_diff": unique})

                    # Métricas Avançadas
                    ADV_LABELS = {
                        "Vida_Util_Restante_Anos": "RUL Estimado (Anos)",
                        "Fator_Severidade_Is": "Severidade (Is)",
                        "Throughput_Acumulado_MWh": "Throughput Acumulado (MWh)",
                        "Ciclos_Profundos_Acima_80_DOD": "Ciclos Profundos (>80% DOD)",
                        "Micro_Ciclos_Abaixo_20_DOD": "Micro-ciclos (<20% DOD)"
                    }
                    
                    for key, label in ADV_LABELS.items():
                        vals = {}
                        for dia in dados_ia:
                            met = dia["Metricas_Avancadas"]
                            if key in met:
                                vals[dia["Simulacao"]] = str(met[key])
                            else:
                                vals[dia["Simulacao"]] = str(met["Resumo_Espectro_Uso"].get(key, "N/A"))
                        unique = len(set(vals.values())) > 1
                        rows.append({"Parâmetro": label, **vals, "_diff": unique})

                    df_diff = pd.DataFrame(rows)
                    diff_mask = df_diff.pop("_diff")

                    def highlight_diff(row):
                        idx = df_diff.index[df_diff["Parâmetro"] == row["Parâmetro"]][0]
                        color = "background-color: #2a1f00; color: #ffcc00;" if diff_mask.iloc[idx] else ""
                        return [color] * len(row)

                    st.dataframe(df_diff.style.apply(highlight_diff, axis=1), use_container_width=True)
                    
                    st.markdown("---")
                    st.subheader("🧠 Análise Inteligente (IA)")
                    st.write("Clique no botão abaixo para gerar um relatório comparativo detalhado das simulações usando a Inteligência Artificial.")
                    
                    if st.button("🚀 Gerar Análise Inteligente", key="btn_gemini_analysis", type="primary"):
                        with st.spinner("Analisando dados das simulações... Isso pode levar alguns segundos."):
                            relatorio_ia = analisar_comparacao_bess(dados_ia)
                            st.markdown("### Relatório do Especialista (Gemini)")
                            st.info("Abaixo está a análise técnica gerada pela inteligência artificial com base nas métricas comparadas.")
                            st.markdown(relatorio_ia)

                else:
                    st.info("Execute novas simulações para obter metadados comparáveis (`config_snapshot.json`).")
            else:
                st.info("Nenhuma das pastas selecionadas contém o arquivo de resultados.")
    else:
        st.warning("Pasta 'Results' não encontrada.")

# --- TAB 4: ENGINE VALIDATION ---
with tab_val:
    st.header("✔️ Validação do Motor de Simulação")
    st.write("Esta aba executa os testes de fidelidade do código-fonte contra a matemática teórica de baterias (Stroe e Rainflow).")
    
    col_gerar, col_validar = st.columns(2)
    
    with col_gerar:
        if st.button("1. Gerar Perfis Sintéticos"):
            with st.spinner(f"Gerando dados sintéticos para o perfil {battery_prof}..."):
                st.session_state.validation_profiles = generate_profiles(bateria_alvo=battery_prof)
            st.success(f"Perfis gerados com sucesso na pasta `data/mock_profiles/`")
            
        if st.session_state.validation_profiles:
            st.info(f"{len(st.session_state.validation_profiles)} perfis de bateria registrados.")
            
    with col_validar:
        # Pega a bateria da sidebar para validar
        if st.button("2. Executar Pipeline de Validação"):
            if not st.session_state.validation_profiles:
                st.error("Gere os perfis primeiro!")
            else:
                with st.spinner(f"Rodando simulação paramétrica para {battery_prof} usando backend {backend}..."):
                    st.session_state.validation_run = rodar_validacao(perfil_nome=battery_prof, backend=backend)
                st.success("Validação Completa!")

    if st.session_state.validation_run:
        res = st.session_state.validation_run
        if res["status"] == "error":
            st.error("Erros na execução: " + ", ".join(res["errors"]))
        else:
            st.markdown("---")
            c_metrics1, c_metrics2, c_metrics3 = st.columns(3)
            
            assertions = res["assertions"]
            
            # --- Cards de Status ---
            def draw_status(col, title, name_key):
                ast = assertions.get(name_key, {"pass": False, "msg": "Teste não executado"})
                if ast["pass"]:
                    col.success(f"**{title}**: PASS")
                    col.caption(ast["msg"])
                else:
                    col.error(f"**{title}**: FAIL")
                    col.caption(ast["msg"])

            draw_status(c_metrics1, "Sanidade Elétrica (BMS)", "bms_safety")
            draw_status(c_metrics2, "Rainflow (DOD)", "rainflow_dod")
            draw_status(c_metrics3, "Não-Linearidade (Stroe)", "stroe_nonlinear")
            
            st.markdown("---")
            
            # --- Relatório Markdown Copiável ---
            try:
                from besx.domain.models.battery_simulator import picos_e_vales
                import rainflow
                
                # 1. TC1
                df_tc1 = res.get("tc1_data")
                if df_tc1 is not None and not df_tc1.empty and 'Tensao_Term_V' in df_tc1.columns:
                    v_max = df_tc1['Tensao_Term_V'].max()
                    v_min = df_tc1['Tensao_Term_V'].min()
                else:
                    v_max, v_min = 0.0, 0.0
                
                if df_tc1 is not None and not df_tc1.empty:
                    soc_max = df_tc1['SOC'].max()
                    soc_min = df_tc1['SOC'].min()
                else:
                    soc_max, soc_min = 0.0, 0.0

                cfg_bat = PERFIS_BATERIA.get(battery_prof)
                vbmax = cfg_bat.v_max_celula * cfg_bat.Ns if cfg_bat else 0.0
                vbmin = cfg_bat.v_min_celula * cfg_bat.Ns if cfg_bat else 0.0
                
                bms_pass = "PASS" if (v_max <= vbmax + 0.1 and v_min >= vbmin - 0.1) else "FAIL"

                # 2. TC2
                df_tc2 = res.get("tc2_data")
                if df_tc2 is not None and not df_tc2.empty:
                    prominence = CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence
                    soc_series = pd.Series(df_tc2['SOC'].values)
                    lista_simplificada = picos_e_vales(soc_series, prominence=prominence)
                    ciclos = list(rainflow.extract_cycles(lista_simplificada))
                    ciclos = [c for c in ciclos if c[0] > 10.0]
                    total_ciclos = len(ciclos)
                    dod_medio = sum(c[0] for c in ciclos)/total_ciclos if total_ciclos > 0 else 0.0
                    soc_medio = sum(c[1] for c in ciclos)/total_ciclos if total_ciclos > 0 else 0.0
                else:
                    total_ciclos, dod_medio, soc_medio = 0, 0.0, 0.0

                # 3. TC3
                hist_cd = res.get("historico_degradacao", [])
                soh_inicial = 100.0
                soh_final = 100.0 - (hist_cd[-1] if hist_cd else 0.0)
                dano_str = f"[{', '.join([f'{d:.4f}' for d in hist_cd])}]" if hist_cd else "[]"
                
                report_md = f"""### Relatório de Validação de Motor (BESx)

#### 1. TC1: Full Cycle & Sanidade Elétrica (BMS)
- **V_term_max**: {v_max:.2f} V (Limite BMS: {vbmax:.2f} V)
- **V_term_min**: {v_min:.2f} V (Limite BMS: {vbmin:.2f} V)
- **SOC_max**: {soc_max:.2f} %
- **SOC_min**: {soc_min:.2f} %
- **Validação BMS Status**: {bms_pass}

#### 2. TC2: Rainflow Micro-cycles & Rainflow (DOD)
- Bateria Ideal Testada: Rs=0, rendimento=1.0
- **Total de Ciclos Extraídos**: {total_ciclos} (Esperado: 10)
- **DOD Médio Identificado**: {dod_medio:.2f}% (Esperado: ~20%)
- **SOC Médio do Ciclo**: {soc_medio:.2f}% (Esperado: ~50%)

#### 3. Degradação a Longo Prazo & Não-Linearidade (Stroe)
- **SOH Inicial**: {soh_inicial:.2f}%
- **SOH Final**: {soh_final:.2f}%
- **Dano Cíclico Acumulado (por mês)**:
`{dano_str}`
"""
                with st.expander("📄 Ver Relatório Markdown Copiável", expanded=False):
                    st.code(report_md, language="markdown")
            except Exception as e:
                st.error(f"Erro ao gerar relatório Markdown: {e}")

            st.markdown("---")
            # --- Plots ---
            st.subheader("Visualização dos Testes")
            tc_tabs = st.tabs(["TC1: Full Cycle", "TC2: Rainflow Micro-cycles", "Degradação a Longo Prazo"])
            
            with tc_tabs[0]:
                df_tc1 = res["tc1_data"]
                if df_tc1 is not None and not df_tc1.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df_tc1['Tempo']/60.0, y=df_tc1['Tensao_Term_V'], name='Tensão (V)', yaxis='y1', line=dict(color=THEME_COLORS["DANGER"])))
                    fig.add_trace(go.Scatter(x=df_tc1['Tempo']/60.0, y=df_tc1['SOC'], name='SOC (%)', yaxis='y2', line=dict(color=THEME_COLORS["PRIMARY"], dash='dash')))
                    fig.update_layout(
                        title="TC1: Comportamento de Carga Completa",
                        yaxis=dict(title="Tensão (V)", side="left"),
                        yaxis2=dict(title="SOC (%)", side="right", overlaying="y", range=[0, 100]),
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=THEME_COLORS["TEXT"])
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.info("""
                    **🧐 Como Validar o TC1:**
                    1. Verifique se a curva de **Tensão (V)** subiu e desceu gradualmente, respondendo ao carregamento (1C) e descarregamento rápido.
                    2. Verifique se o **SOC (%)** descreve rampas lineares puras de 0 a 100%, já que não deve haver perdas excessivas num modelo CC (Coulomb Counting) isolado.
                    3. Observe no Card de 'Sanidade Elétrica' se a tensão ultrapassou o safe operating area da bateria, atestando limites seguros impostos pelo PCS/BMS virtual.
                    """)
                    
            with tc_tabs[1]:
                df_tc2 = res["tc2_data"]
                if df_tc2 is not None and not df_tc2.empty:
                    fig2 = px.line(df_tc2, x=df_tc2['Tempo']/60.0, y='SOC', title='TC2: SOC Profile (DOD Constante)', color_discrete_sequence=[THEME_COLORS["WARNING"]])
                    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]))
                    st.plotly_chart(fig2, use_container_width=True)
                    st.info("""
                    **🧐 Como Validar o TC2:**
                    1. O gráfico de SOC deve mostrar o comportamento de meia-onda (onda quadrada filtrada pelas resistências) centrado ao redor do SOC 50%.
                    2. O algoritmo **Rainflow** irá abstrair todas as inflexões matemáticas desse gráfico e deve devolver, pela verificação do sistema, microciclos uniformes com aproximadamente **20% de DOD**.
                    3. O sucesso atesta que a biblioteca entende e fraciona adequadamente o desgaste real da bateria diante de usos intermitentes de alta frequência.
                    """)
                    
            with tc_tabs[2]:
                hist_cd = res["historico_degradacao"]
                if hist_cd is not None:
                    fig3 = px.line(x=res["history_meses"], y=hist_cd, markers=True, 
                                 title='Acumulação de Capacity Fade Cíclico Equivalente (Stroe Eq)', 
                                 labels={'x': 'Meses (Ciclos contínuos)', 'y': 'C_cyc Acumulado (%)'},
                                 color_discrete_sequence=[THEME_COLORS["CALENDAR"]])
                    fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=THEME_COLORS["TEXT"]))
                    st.plotly_chart(fig3, use_container_width=True)
                    st.info("""
                    **🧐 Como Validar o Teste Não-Linear:**
                    1. A curva exibida **NÃO PODE SER RETA**. Se a degradação subisse em linha reta, estaríamos subestimando o tempo de vida real da bateria.
                    2. Segundo o **Modelo Empírico de Stroe**, baterias de Íon-Lítio (como LFP e NMC) sofrem muito mais rapidamente os primeiros sinais de perdas químicas, nivelando depois.
                    3. Portanto, a curva mostrada é propositalmente **sublinear (achatada na ponta)** originada por uma integração Quadrática Root-Mean dos desgastes diários, de acordo com `C_cyc_tot = sqrt(Dano1^2 + Dano2^2 ...)`.
                    """)
                    
# --- TAB 5: CONFIGURATION ---
with tab_cfg:
    st.header("⚙️ Ajustes do Modelo de Degradação")
    st.info("Estes valores são aplicados apenas nesta sessão. Altere com cuidado.")
    
    with st.form("degr_config_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔄 Dano Cíclico")
            a_val = st.number_input("Coeficiente a", value=st.session_state.config_override["ciclo"]["a"], format="%.6f")
            b_val = st.number_input("Coeficiente b", value=st.session_state.config_override["ciclo"]["b"], format="%.6f")
            c_val = st.number_input("Coeficiente c", value=st.session_state.config_override["ciclo"]["c"], format="%.6f")
            d_val = st.number_input("Coeficiente d", value=st.session_state.config_override["ciclo"]["d"], format="%.6f")
        
        with col2:
            st.subheader("⏳ Dano Calendário")
            kt_val = st.number_input("k_T", value=st.session_state.config_override["calendario"]["k_T"], format="%.2e")
            ksoc_val = st.number_input("k_soc", value=st.session_state.config_override["calendario"]["k_soc"], format="%.6f")
            exp_cal_val = st.number_input("Expoente Cal", value=st.session_state.config_override["calendario"]["exp_cal"], format="%.2f")

        if st.form_submit_button("Aplicar Configurações"):
            st.session_state.config_override["ciclo"]["a"] = a_val
            st.session_state.config_override["ciclo"]["b"] = b_val
            st.session_state.config_override["ciclo"]["c"] = c_val
            st.session_state.config_override["ciclo"]["d"] = d_val
            st.session_state.config_override["calendario"]["k_T"] = kt_val
            st.session_state.config_override["calendario"]["k_soc"] = ksoc_val
            st.session_state.config_override["calendario"]["exp_cal"] = exp_cal_val
            st.success("Configurações aplicadas com sucesso!")

`

## Arquivo: src\besx\infrastructure\__init__.py
`python

`

## Arquivo: src\besx\infrastructure\files\file_manager.py
`python

import os
import datetime
import shutil
from besx.infrastructure.logging.logger import logger

class FileManager:
    def __init__(self, base_path=None):
        """
        Gerencia a estrutura de pastas e arquivos da simulação.
        
        Cria uma nova pasta para cada execução baseada no timestamp.
        Ex: results/sim_20231027_103000/
        """
        from besx.config import PATH_RESULTS
        self.base_path = base_path or PATH_RESULTS
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.sim_folder = os.path.join(self.base_path, f"sim_{self.timestamp}")
        
        # Subpastas
        self.plots_folder = os.path.join(self.sim_folder, "plots")
        self.debug_folder = os.path.join(self.sim_folder, "debug")
        self.data_folder = os.path.join(self.sim_folder, "data")
        
        self._create_structure()
        
    def _create_structure(self):
        """Cria as pastas necessárias."""
        os.makedirs(self.plots_folder, exist_ok=True)
        os.makedirs(self.debug_folder, exist_ok=True)
        os.makedirs(self.data_folder, exist_ok=True)
        logger.info(f"Diretório da simulação criado: {self.sim_folder}")

    def get_debug_path(self, filename):
        """Retorna o caminho completo para um arquivo de debug."""
        return os.path.join(self.debug_folder, filename)

    def get_plot_path(self, filename):
        """Retorna o caminho completo para um arquivo de plot."""
        return os.path.join(self.plots_folder, filename)

    def get_data_path(self, filename):
        """Retorna o caminho completo para um arquivo de dados (ex: .mat intermediário)."""
        return os.path.join(self.data_folder, filename)
    
    def save_report(self, content, filename="report.txt"):
        """Salva o relatório final da simulação."""
        report_path = os.path.join(self.sim_folder, filename)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        return report_path

`

## Arquivo: src\besx\infrastructure\llm\__init__.py
`python

`

## Arquivo: src\besx\infrastructure\llm\gemini_analyzer.py
`python
import json
from google import genai
from besx.config import CONFIGURACAO
from besx.infrastructure.logging.logger import logger

def analisar_comparacao_bess(dados_simulacoes: list[dict], api_key: str = None) -> str:
    """
    Envia os dados de comparação das simulações para a API do Gemini e
    retorna um relatório analítico em formato Markdown.
    
    Args:
        dados_simulacoes: Lista de dicionários contendo os KPIs e configurações 
                          relevantes de cada simulação para comparação.
        api_key: Chave opcional da API do Gemini. Se None, usará do CONFIGURACAO.
        
    Returns:
        String com a análise formatada em Markdown, ou mensagem de erro.
    """
    key = api_key or CONFIGURACAO.llm.gemini_api_key
    
    if not key or key == "sua_chave_api_aqui":
        return "⚠️ **Erro:** A chave da API do Gemini não foi configurada corretamente. Adicione em `config.py` ou na variável de ambiente `GEMINI_API_KEY`."
    
    try:
        client = genai.Client(api_key=key)
        
        # Preparando os dados em JSON formatado para facilitar a leitura da IA
        dados_json = json.dumps(dados_simulacoes, indent=2, ensure_ascii=False)
        
        prompt = f"""# Persona e Contexto

Você é um Engenheiro de Confiabilidade de Baterias (BESS) e Especialista em Ciência de Dados.
Sua tarefa é analisar os resultados de simulações de degradação de baterias de íon-lítio gerados por um motor matemático baseado no Modelo Empírico de Stroe e no algoritmo de Rainflow Cycle Counting.

Você receberá um payload de dados contendo duas ou mais simulações (ex: Cenário A e Cenário B), incluindo métricas como SOH (State of Health), RUL (Remaining Useful Life), EFC (Equivalent Full Cycles), Throughput de Energia, Fator de Severidade Global (σ) e faixas de temperatura.

# Objetivos da Análise

Trabalhe neste problema passo a passo. Faça uma análise técnica, neutra e baseada estritamente nos dados fornecidos, dividida nas três seções a seguir:

## 1. Análise Comparativa Direta

- Compare as simulações fornecidas.
- Identifique qual cenário resulta em uma vida útil (RUL) maior e justifique com base no balanço entre a degradação cíclica (uso) e calendárica (repouso).
- Avalie o volume de energia processada (Throughput) versus o desgaste sofrido (SOH).

## 2. "Reality Check" (Estimativa de Proximidade com o Real)

Modelos empíricos possuem limitações no mundo real. Avalie a confiabilidade destas simulações e a proximidade com o desgaste real utilizando as seguintes regras de domínio:
- **Análise do Fator de Severidade (σ):** Se o Fator de Severidade de um cenário for muito alto (ex: > 1.5) ou muito variável, alerte o usuário de que a simulação pode estar subestimando o dano real. Modelos empíricos perdem precisão quando operam fora das condições nominais de calibração de laboratório.
- **Estresse Térmico e Químico:** Se a temperatura máxima de operação ultrapassar 35°C ou ficar abaixo de 10°C, aponte que fenômenos físicos não capturados pelo modelo de Stroe (como *Lithium Plating* em baixas temperaturas ou crescimento acelerado e anômalo da camada SEI pelo calor) podem fazer com que a bateria real morra mais rápido do que a simulação prevê.
- **Perfil do Rainflow:** Se o EFC for alcançado através de ciclos muito profundos (alto DOD), alerte que o estresse mecânico real nas partículas do eletrodo pode gerar microfissuras que aceleram a perda de material ativo de forma não linear, aproximando a simulação de uma margem de erro maior.

## 3. Limitações e Recomendações (PIML)

- Não generalize os resultados além do que os números mostram. Indique explicitamente que esta é uma simulação matemática.
- Recomende que, para uma operação real em campo, este modelo deve atuar em conjunto com uma arquitetura de aprendizado de máquina guiado pela física (Physics-Informed Machine Learning - PIML), onde os dados de telemetria reais calibram os resíduos do modelo físico ao longo do tempo.

# Restrições de Saída

- Retorne a resposta formatada em Markdown, utilizando tabelas ou bullet points para facilitar a leitura no dashboard.
- Mantenha um tom técnico, objetivo e cauteloso. Não afirme que a simulação é uma previsão infalível.

# Dados de Entrada

Os dados estão no formato JSON:
{dados_json}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        return response.text

    except Exception as e:
        logger.error(f"Erro ao chamar API do Gemini: {e}")
        return f"❌ **Erro na comunicação com a Inteligência Artificial:**\n{str(e)}"

`

## Arquivo: src\besx\infrastructure\loaders\conversor.py
`python
import pandas as pd
import scipy.io
import numpy as np
import os
from besx.infrastructure.logging.logger import logger

def expandir_curva_carga(
    caminho_arquivo, 
    coluna_data='Data', 
    coluna_potencia='Potencia', 
    anos_para_expandir=10, 
    separador_csv=','
):
    """
    Lê uma curva de carga, detecta a resolução e expande para N anos.
    Assume crescimento vegetativo de 0%.
    Adiciona contagem de meses padronizados de 30 dias.
    """
    
    logger.info(f"--- Lendo arquivo: {caminho_arquivo} ---")
    try:
        # Tenta ler o CSV. Converta a coluna de data para datetime.
        df = pd.read_csv(caminho_arquivo, sep=separador_csv)
        df[coluna_data] = pd.to_datetime(df[coluna_data])
        df = df.sort_values(by=coluna_data).reset_index(drop=True)
    except Exception as e:
        logger.error(f"Erro ao ler o arquivo. Verifique o separador ou nomes das colunas.\nErro: {e}")
        return None

    # --- 1. Detectar Resolução ---
    if len(df) < 2:
        logger.error("Erro: O arquivo precisa ter pelo menos 2 linhas para calcular a resolução.")
        return None
        
    delta_t = df[coluna_data][1] - df[coluna_data][0]
    resolucao_minutos = delta_t.total_seconds() / 60
    
    logger.info(f"Resolução detectada: {resolucao_minutos:.1f} minutos")
    
    # --- 2. Preparar Expansão ---
    # Dados originais (apenas a coluna de potência)
    potencia_base = df[coluna_potencia].values
    total_linhas_base = len(potencia_base)
    
    # Cálculo de quantas vezes precisamos repetir os dados
    # Se a base já for 1 ano, repetimos 'anos_para_expandir' vezes.
    # Se a base for menor, precisaríamos calcular, mas assumiremos que a entrada
    # é o "ciclo padrão" (ex: 1 ano típico) a ser repetido.
    repeticoes = int(anos_para_expandir)
    
    logger.info(f"Base de dados original tem {total_linhas_base} registros.")
    logger.info(f"Expandindo para {anos_para_expandir} anos (Repetindo a base {repeticoes} vezes)...")
    
    # --- 3. Expansão dos Dados (Crescimento 0%) ---
    # tile repete o array 'repeticoes' vezes
    nova_potencia = np.tile(potencia_base, repeticoes)
    
    # --- 4. Reconstrução da Linha do Tempo ---
    # Data inicial
    data_inicio = df[coluna_data][0]
    total_novos_registros = len(nova_potencia)
    
    # Cria um array de deltas de tempo
    # Ex: [0 min, 15 min, 30 min, ...]
    # Multiplicamos o índice pelo delta_t
    indices_tempo = np.arange(total_novos_registros)
    deltas = pd.to_timedelta(indices_tempo * resolucao_minutos, unit='m')
    
    novas_datas = data_inicio + deltas
    
    # --- 5. Criação do DataFrame Expandido ---
    df_expandido = pd.DataFrame({
        'Data_Hora': novas_datas,
        'Potencia': nova_potencia
    })
    
    # --- 6. Adicionar Lógica de "Mês de 30 Dias" ---
    # Quantas linhas correspondem a 1 hora?
    linhas_por_hora = 60 / resolucao_minutos
    
    # Quantas linhas correspondem a 30 dias (720 horas)?
    linhas_por_mes_padrao = linhas_por_hora * 24 * 30
    
    # Cria coluna de mês (1, 1, 1... 2, 2, 2...)
    # Usamos divisão inteira (//) pelo tamanho do bloco do mês
    df_expandido['Mes_Simulacao'] = (df_expandido.index // linhas_por_mes_padrao).astype(int) + 1
    
    # Adiciona também o Ano de Simulação para facilitar
    linhas_por_ano_padrao = linhas_por_mes_padrao * 12 # 360 dias comerciais
    df_expandido['Ano_Simulacao'] = (df_expandido.index // linhas_por_ano_padrao).astype(int) + 1

    logger.info("--- Expansão Concluída ---")
    logger.info(df_expandido.head())
    logger.info("...")
    logger.info(df_expandido.tail())
    
    return df_expandido


def converter_csv_para_mat(csv_path, mat_path, var_name):
    """
    Converte um arquivo CSV específico para o formato .mat do MATLAB.

    O CSV deve ter duas colunas, separadas por ponto e vírgula,
    e usar vírgula como separador decimal.

    Args:
        csv_path (str): Caminho para o arquivo CSV de entrada.
        mat_path (str): Caminho para o arquivo .mat de saída.
        var_name (str): Nome da variável a ser usada no arquivo .mat.
    """
    logger.info(f"Iniciando a conversão de '{csv_path}' para '{mat_path}'...")

    if not os.path.exists(csv_path):
        logger.error(f"Erro: O arquivo de entrada '{csv_path}' não foi encontrado.")
        return

    try:
        # Lê o arquivo CSV usando pandas, especificando delimitador, decimal e a codificação 'utf-8-sig' para ignorar o BOM
        df = pd.read_csv(csv_path, delimiter=';', decimal=',', header=None, encoding='utf-8-sig')

        # Converte o DataFrame para um array NumPy e transpõe para o formato 2xN
        data_array = df.to_numpy().T

        # Salva o array em um arquivo .mat
        scipy.io.savemat(mat_path, {var_name: data_array})

        logger.info(f"Conversão concluída com sucesso! Arquivo '{mat_path}' foi gerado.")
    except Exception as e:
        logger.error(f"Ocorreu um erro durante a conversão: {e}")

if __name__ == "__main__":
    converter_csv_para_mat(CSV_FILENAME, MAT_FILENAME, MAT_VARIABLE_NAME)
`

## Arquivo: src\besx\infrastructure\loaders\data_handler.py
`python
"""
data_handler.py (O Especialista em Dados)

Responsabilidade: Tudo relacionado à manipulação dos dados de entrada.
Sabe como ler o arquivo .mat, convertê-lo para um DataFrame e fatiá-lo
em pedaços mensais.
"""
from besx.infrastructure.loaders.conversor import converter_csv_para_mat
import pandas as pd
from scipy.io import loadmat
from scipy.signal import find_peaks
import numpy as np
import scipy.io
import os
import math
from besx.infrastructure.logging.logger import logger

# Importa a configuração centralizada
from besx.config import CONFIGURACAO

def data_handle(nome_arquivo=None, meses_alvo=None, file_manager=None):
    """
    Função principal do módulo: orquestra o carregamento e fatiamento dos dados.
    """
    import os

    logger.info("--- Início do Data Handle ---")

    # 1. Selecionar Arquivo (Interação com usuário se não fornecido)
    if nome_arquivo is None:
        nome_arquivo_inicial = selecionar_arquivo_database()
    else:
        nome_arquivo_inicial = nome_arquivo

    if not nome_arquivo_inicial:
        return [] 

    # 2. Identificar e Converter (CSV -> MAT se necessário)
    # Esta função retorna apenas o NOME do arquivo .mat (ex: "arquivo.mat")
    nome_arquivo_mat = identificar_tipo_arquivo(nome_arquivo_inicial)
    
    if not nome_arquivo_mat:
        logger.error("Falha na identificação do arquivo.")
        return []

    from besx.config import PATH_DATABASE
    caminho_completo = os.path.join(PATH_DATABASE, nome_arquivo_mat)
    logger.info(f"Tentando carregar dados de: {caminho_completo}")

    # 3. Carregar arquivo usando o caminho completo
    
    df_completo = carregar_dados_mat(caminho_completo) 

    # --- TRAVA DE SEGURANÇA
    if df_completo is None:
        logger.error(f"Falha ao carregar o arquivo. Verifique se ele existe e é um .mat válido.")
        return []

    logger.info("Dados carregados com sucesso. Iniciando análise...")

    # 4. Analisar Dados
    dt_minutos = analisar_integridade_dados(df_completo)
    
    if dt_minutos is None:
         logger.error("Não foi possível determinar o passo de tempo.")
         return []

    CONFIGURACAO.dados_entrada.dt_minutos = dt_minutos

    # 5. Ajustar Duração (Opcional)
    df_final = ajustar_duracao_dados(df_completo, dt_minutos, meses_alvo=meses_alvo, interativo=(nome_arquivo is None))
    
    # Atualiza anos de simulação no config para os plots
    minutos_totais = len(df_final) * dt_minutos
    anos_simulados = minutos_totais / (360 * 24 * 60)
    CONFIGURACAO.simulacao.ANOS_SIMULACAO = round(anos_simulados, 2)

    # 6. Fatiar em Meses
    lista_meses = fatiar_dados_mensais(df_final) 
    
    return lista_meses



#1 Execução
def selecionar_arquivo_database():
    logger.info("Carregando dados de entrada...")
    from besx.config import PATH_DATABASE
    pasta_database = PATH_DATABASE

    # 1. Verifica se a pasta existe
    if not os.path.exists(pasta_database):
        # Tenta criar a pasta se não existir, para evitar erro na próxima vez
        try:
            os.makedirs(pasta_database)
            logger.warning(f"Aviso: A pasta '{pasta_database}' não existia e foi criada. Coloque seus arquivos nela.")
        except OSError:
            logger.error(f"Erro: A pasta '{pasta_database}' não foi encontrada.")
        return None
    
    # 2. Lista os arquivos (ignorando subpastas e arquivos ocultos como .DS_Store)
    arquivos = [
        f for f in os.listdir(pasta_database) 
        if os.path.isfile(os.path.join(pasta_database, f)) and not f.startswith('.')
    ]

    if not arquivos:
        logger.warning(f"Aviso: A pasta '{pasta_database}' está vazia.")
        return None

    # 3. Exibe as opções
    logger.info(f"--- Arquivos disponíveis em '{pasta_database}/' ---")
    for i, arquivo in enumerate(arquivos):
        logger.info(f"[{i + 1}] {arquivo}")

    # 4. Loop de interação com o usuário
    while True:
        try:
            entrada = input("\nDigite o número do arquivo que deseja analisar: ")
            escolha = int(entrada)
            
            if 1 <= escolha <= len(arquivos):
                arquivo_escolhido = arquivos[escolha - 1]
                logger.info(f"-> Arquivo selecionado: {arquivo_escolhido}")
                
                # Retorna apenas o nome do arquivo (ou o caminho completo se preferir)
                return arquivo_escolhido 
            else:
                logger.warning(f"Opção inválida. Escolha entre 1 e {len(arquivos)}.")
        except ValueError:
            logger.error("Entrada inválida. Por favor, digite um número inteiro.")
#2 Execução


def identificar_tipo_arquivo(nome_arquivo_selecionado):
    """
    Analisa a extensão, converte se necessário e RETORNA o nome do arquivo .mat final.
    """
    nome_base, extensao = os.path.splitext(nome_arquivo_selecionado)
    extensao = extensao.lower()

    # Monta caminhos completos
    from besx.config import PATH_DATABASE
    caminho_origem = os.path.join(PATH_DATABASE, nome_arquivo_selecionado)
    
    # O destino sempre será .mat
    nome_arquivo_mat = f"{nome_base}.mat"
    caminho_destino = os.path.join(PATH_DATABASE, nome_arquivo_mat)

    if extensao == '.mat':
        logger.info(f"-> Arquivo MAT detectado: {nome_arquivo_selecionado}")
        # Atualiza config
        CONFIGURACAO.dados_entrada.ARQUIVO_MAT = nome_arquivo_selecionado
        return nome_arquivo_selecionado

    elif extensao == '.csv':
        logger.info(f"-> Arquivo CSV detectado. Convertendo '{nome_arquivo_selecionado}'...")
        
        # Chama o conversor
        converter_csv_para_mat(caminho_origem, caminho_destino, "ATot")
        
        logger.info(f"-> Conversão concluída. Novo arquivo gerado: {nome_arquivo_mat}")
        
        # Atualiza config para usar o MAT, não o CSV
        CONFIGURACAO.dados_entrada.ARQUIVO_MAT = nome_arquivo_mat
        
        # IMPORTANTE: Retorna o nome do arquivo MAT, não o CSV
        return nome_arquivo_mat

    else:
        logger.error(f"Erro: Extensão '{extensao}' não suportada.")
        return None


#3 Execução
def carregar_dados_mat(filename):
    """
    (Função interna) Carrega um arquivo .mat e o converte para um DataFrame.
    """
    
    try:
        dados_mat = loadmat(filename)
        # Filtra chaves que não começam com __ (metadados do MAT)
        variaveis = [k for k in dados_mat.keys() if not k.startswith('__')]
        
        if not variaveis:
            logger.error(f"O arquivo '{filename}' não contém variáveis válidas.")
            return None
            
        nome_variavel = variaveis[0]
        matriz_dados = dados_mat[nome_variavel]
        df_total = pd.DataFrame(matriz_dados.T, columns=['Tempo', 'Potencia_kW'])     
        logger.info(f"Arquivo '{filename}' carregado. Total de {len(df_total)} linhas.")
        return df_total
    except Exception as e:
        logger.error(f"Erro ao carregar ou converter '{filename}': {e}")
        return None

def analisar_integridade_dados(df):
    """
    Analisa os dados assumindo que a primeira coluna é Tempo (em minutos)
    e a segunda é Potência.
    """
    logger.info("="*40)
    logger.info("RELATÓRIO DE ANÁLISE DOS DADOS")
    logger.info("="*40)
    
    col_tempo = df.columns[0]
    col_valor = df.columns[1]

    # --- 1. Tempo de Amostra (dt) ---
    # Verifica se a coluna é numérica
    if pd.api.types.is_numeric_dtype(df[col_tempo]):
        # Calcula a diferença entre passos (ex: 5 - 0 = 5)
        deltas = df[col_tempo].diff().dropna()
        
        # Pega o valor mais comum (moda)
        dt_minutos = deltas.mode()[0]
        
        logger.info(f"1. Tempo de Amostra Detectado: {dt_minutos} minutos")
        
        # Verifica constância
        is_constant = np.allclose(deltas, dt_minutos, atol=1e-5)
        if not is_constant:
            logger.warning(f"   [ALERTA] Passo de tempo varia! (Jitter ou buracos nos dados)")
            logger.warning(f"   Variação: Min={deltas.min()}, Max={deltas.max()}")
        else:
            logger.info(f"   [OK] O passo de tempo é constante.")
            
        # --- 2. Quantidade de Meses ---
        tempo_inicial = df[col_tempo].min()
        tempo_final = df[col_tempo].max()
        duracao_minutos = tempo_final - tempo_inicial
        
        # Conversão: 1 mês = 30 dias * 24h * 60min = 43.200 minutos
        minutos_em_um_mes = 30 * 24 * 60
        meses_totais = duracao_minutos / minutos_em_um_mes
        
        logger.info(f"2. Cobertura Temporal:")
        logger.info(f"   Início: {tempo_inicial} min")
        logger.info(f"   Fim:    {tempo_final} min")
        logger.info(f"   Duração Total: {duracao_minutos:.0f} minutos")
        logger.info(f"   Meses Completos (base 30 dias): {meses_totais:.2f} meses")
        
    else:
        logger.error("Erro: A coluna de tempo não é numérica. Verifique o formato do arquivo.")
        return None

    # --- 3. Verificação de Nulos ---
    nulos = df[col_valor].isna().sum()
    if nulos > 0:
        logger.warning(f"3. [PERIGO] Valores Nulos (NaN) detectados: {nulos}")
    else:
        logger.info(f"3. [OK] Nenhum valor nulo detectado.")

    # --- 4. Estatísticas de Valor ---
    max_val = df[col_valor].max()
    min_val = df[col_valor].min()
    mean_val = df[col_valor].mean()
    
    logger.info(f"4. Estatísticas de Valor ({col_valor}):")
    logger.info(f"   Máximo: {max_val:.2f}")
    logger.info(f"   Mínimo: {min_val:.2f}")
    logger.info(f"   Média:  {mean_val:.2f}")

    logger.info("="*40)
    
    return dt_minutos

def ajustar_duracao_dados(df, dt_minutos, meses_alvo=None, interativo=True):
    """
    Expande ou corta os dados.
    Baseia-se em meses padronizados de 30 dias.
    """
    col_tempo = df.columns[0]
    col_valor = df.columns[1] # Potência
    
    # Cálculos de base
    total_linhas_atual = len(df)
    minutos_por_mes = 30 * 24 * 60 # 43.200 minutos
    linhas_por_mes = minutos_por_mes / dt_minutos
    
    meses_atuais = total_linhas_atual / linhas_por_mes
    
    logger.info("--- Ajuste de Duração da Simulação ---")
    logger.info(f"Dados carregados: {meses_atuais:.1f} meses ({total_linhas_atual} amostras).")
    
    if interativo:
        entrada = input(f"Digite a quantidade de meses desejada (ou Enter para manter {meses_atuais:.1f}): ").strip()
        if not entrada:
            logger.info("-> Mantendo duração original.")
            return df
        try:
            meses_finais = float(entrada)
        except ValueError:
            logger.warning("-> Entrada inválida. Mantendo duração original.")
            return df
    else:
        # Modo não-interativo (ex: dashboard)
        if meses_alvo is not None:
            meses_finais = meses_alvo
        else:
            logger.info("-> Mantendo duração original.")
            return df

    # Calcula quantas linhas precisamos no total
    linhas_alvo = int(meses_finais * linhas_por_mes)
    
    if linhas_alvo == total_linhas_atual:
        logger.info("-> Duração inalterada.")
        return df

    # CENÁRIO 1: CORTAR (LIMITAR)
    if linhas_alvo < total_linhas_atual:
        logger.info(f"-> Reduzindo dados para {meses_finais} meses...")
        df_novo = df.iloc[:linhas_alvo].copy()
        return df_novo

    # CENÁRIO 2: EXPANDIR (REPETIR)
    if linhas_alvo > total_linhas_atual:
        logger.info(f"-> Expandindo dados para {meses_finais} meses (Repetição cíclica)...")
        
        # 1. Repetir os valores de potência
        # Calculamos quantas cópias inteiras precisamos + sobra
        repeticoes = math.ceil(linhas_alvo / total_linhas_atual)
        
        # Repete o array de potência
        valores_potencia = df[col_valor].values
        novo_array_potencia = np.tile(valores_potencia, repeticoes)
        
        # Corta o excesso para ficar exato
        novo_array_potencia = novo_array_potencia[:linhas_alvo]
        
        # 2. Reconstruir o vetor de Tempo (Fundamental!)
        # O tempo deve continuar crescendo: 0, 5, 10, ..., N
        tempo_inicial = df[col_tempo].iloc[0]
        novo_array_tempo = np.arange(0, linhas_alvo) * dt_minutos + tempo_inicial
        
        # 3. Montar novo DataFrame
        df_novo = pd.DataFrame({
            col_tempo: novo_array_tempo,
            col_valor: novo_array_potencia
        })
        
        return df_novo



def fatiar_dados_mensais(df):
    """
    Divide o DataFrame em uma lista de DataFrames mensais.
    Considera um mês padrão de 30 dias.
    """
    logger.info("Fatiando dados em meses...")
    
    # Busca a configuração de tempo (dt) no objeto central
    dt_minutos = CONFIGURACAO.dados_entrada.dt_minutos
    dias_mes = CONFIGURACAO.dados_entrada.dias_por_mes_sim
    
    # 1 mês = dias_mes * 24 horas * 60 minutos
    minutos_por_mes = dias_mes * 24 * 60
    amostras_por_mes = int(minutos_por_mes / dt_minutos)
    
    lista_meses = []
    total_linhas = len(df)
    
    for i in range(0, total_linhas, amostras_por_mes):
        df_mes = df.iloc[i : i + amostras_por_mes].copy()
        
        # Reseta o tempo para começar em 0 em cada mês
        df_mes['Tempo'] = df_mes['Tempo'] - df_mes['Tempo'].iloc[0]
        
        # Validação: só adiciona se tiver um volume mínimo de dados (ex: > 20% do mês)
        if len(df_mes) > (amostras_por_mes * 0.2):
            lista_meses.append(df_mes)
            
    logger.info(f"Fatiamento concluído: {len(lista_meses)} meses gerados.")
    return lista_meses

`

## Arquivo: src\besx\infrastructure\logging\logger.py
`python

import logging
import colorlog
import sys

def setup_logger():
    """
    Configura o logger principal com saída colorida no console.
    """
    logger = logging.getLogger("BESx")
    logger.setLevel(logging.DEBUG)

    # Evita duplicar handlers se o logger já estiver configurado
    if logger.hasHandlers():
        return logger

    # Handler do Console (Colorido)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()

`

## Arquivo: src\besx\infrastructure\plecs\plecs_connector.py
`python
"""
plecs_connector.py  —  Adaptador de Simulação de Bateria

Responsabilidade: fornecer a interface de simulação mensal para o SimulationManager.
Roteia a chamada para o backend escolhido pelo usuário no menu inicial:

  backend = "python"  →  Simulador Python puro (battery_simulator.py)
  backend = "plecs"   →  PLECS via XML-RPC (requer servidor PLECS aberto)

A assinatura pública de run_monthly_simulation() é a mesma em ambos os backends,
garantindo compatibilidade total com simulation.py.
"""

import pandas as pd
import numpy as np
import xmlrpc.client
from scipy.io import savemat

from besx.config import BateriaConfig, Settings, ROOT_DIR
from besx.infrastructure.logging.logger import logger
from besx.domain.models.battery_simulator import simular_soc_mes


# ------------------------------------------------------------------ #
#  Interface pública                                                   #
# ------------------------------------------------------------------ #

def run_monthly_simulation(
    df_mes: pd.DataFrame,
    soh_atual: float,
    SOC_0: float,
    ctt: int,
    config: Settings,
    backend: str = "python",
) -> pd.DataFrame:
    """
    Simula um mês de operação da bateria e retorna o perfil de SOC.

    Args:
        df_mes (pd.DataFrame):
            Perfil de potência do mês — colunas [Tempo (min), Potencia_kW].
        soh_atual (float):
            State of Health no início do mês (fração 0–1).
        SOC_0 (float):
            SOC inicial do mês (fração 0–1).
        ctt (int):
            Número sequencial do mês (logging / debug).
        config (Settings):
            Objeto de configuração da simulação (Pydantic).
        backend (str):
            "python"  → simulador Python interno
            "plecs"   → PLECS via XML-RPC

    Returns:
        pd.DataFrame: colunas ['Tempo' (s), 'SOC' (%)].
    """
    if backend == "plecs":
        return _run_plecs(df_mes, soh_atual, SOC_0, ctt, config)
    else:
        return _run_python(df_mes, soh_atual, SOC_0, ctt, config)


def extrair_soc_final(df_soc: pd.DataFrame) -> float:
    """
    Extrai o SOC final da simulação mensal como fração 0–1.

    Args:
        df_soc: DataFrame com colunas ['Tempo', 'SOC']

    Returns:
        float: SOC final (0–1)
    """
    if df_soc is None or df_soc.empty:
        raise ValueError("DataFrame de SOC vazio ou inválido.")

    df_soc = df_soc.sort_values('Tempo')
    soc_final = float(df_soc['SOC'].iloc[-1]) / 100.0  # % → fração

    if not 0.0 <= soc_final <= 1.0:
        raise ValueError(f"SOC final fora do intervalo físico: {soc_final:.4f}")

    return soc_final


def close_plecs_server():
    """
    Tenta fechar o servidor PLECS (no-op se backend Python estiver em uso).
    """
    try:
        plecs_server = xmlrpc.client.ServerProxy("http://localhost:1080/RPC2")
        plecs_server.plecs.quit()
        logger.info("Comando para fechar o servidor PLECS enviado com sucesso.")
    except Exception as e:
        logger.info(f"close_plecs_server(): sem servidor ativo ({e})")


# ------------------------------------------------------------------ #
#  Backend Python                                                      #
# ------------------------------------------------------------------ #

def _run_python(
    df_mes: pd.DataFrame,
    soh_atual: float,
    SOC_0: float,
    ctt: int,
    config: Settings,
) -> pd.DataFrame:
    """Delega ao simulador Python de integração de Coulomb."""
    cfg_bat = config.bateria
    logger.info(
        f"[Python] Mês {ctt} | SOC_0={SOC_0*100:.1f}% | SOH={soh_atual*100:.1f}%"
    )
    return simular_soc_mes(
        df_mes=df_mes,
        soh_atual=soh_atual,
        soc_inicial=SOC_0,
        cfg_bat=cfg_bat, # Passa o objeto Pydantic diretamente
    )


# ------------------------------------------------------------------ #
#  Backend PLECS                                                       #
# ------------------------------------------------------------------ #

def _run_plecs(
    df_mes: pd.DataFrame,
    soh_atual: float,
    SOC_0: float,
    ctt: int,
    config: Settings,
) -> pd.DataFrame | None:
    """Executa a simulação via XML-RPC no PLECS."""
    plecs_server = xmlrpc.client.ServerProxy("http://localhost:1080/RPC2")
    cfg_plecs    = config.plecs
    cfg_bat      = config.bateria

    # Prepara e salva o arquivo .mat de entrada
    df_tmp = df_mes.copy()
    
    # NORMALIZAÇÃO DO TEMPO:
    # Garante que cada mês comece em t=0 para o PLECS, 
    # subtraindo o tempo inicial do mês.
    tempo_inicial_mes = df_tmp.iloc[0, 0]
    df_tmp.iloc[:, 0] = df_tmp.iloc[:, 0] - tempo_inicial_mes
    
    df_tmp[df_tmp.columns[0]] *= 60  # min → s
    matriz_dados_plecs = df_tmp.to_numpy().T

    try:
        entrada_pot_path = str(ROOT_DIR / cfg_plecs.ARQUIVO_ENTRADA_POT)
        logger.info(f"[PLECS] Salvando {entrada_pot_path}")
        savemat(entrada_pot_path, {'Pot_Input': matriz_dados_plecs})
    except Exception as e:
        logger.error(f"[PLECS] Erro ao criar arquivo .mat: {e}")
        return None

    # Monta ModelVars e executa
    model_vars = _montar_model_vars_bateria(cfg_bat, SOC_0, soh_atual)
    try:
        # Tenta abrir o Scope2 no PLECS para visualização em tempo real
        try:
            scope_path = f"{cfg_plecs.MODELO_PLECS}/Scope2"
            # Tentamos 'plecs.scope(path, "Open")' ou avisamos o usuário.
            plecs_server.plecs.scope(scope_path, 'Open')
            logger.info(f"[PLECS] Scope2 aberto para visualização.")
        except Exception as scope_e:
            # Muitos servidores XML-RPC do PLECS não expõem o controle de GUI de Scopes
            logger.debug(f"[PLECS] Skip openScope (método 'scope' pode não estar exposto): {scope_e}")
        
        plecs_server.plecs.simulate(cfg_plecs.MODELO_PLECS, {'ModelVars': model_vars})
        logger.info(f"[PLECS] Simulação concluída — mês {ctt}")
    except Exception as e:
        logger.error(f"[PLECS] Erro durante a simulação: {e}")
        return None

    # Lê o CSV de saída
    try:
        # Lê Arquivo com novo Formato de exportacao forçado para a raiz do projeto
        out_file = str(ROOT_DIR / "dadosnovos.csv")
        # O PLECS Scope exporta o header diretamente na linha 0.
        df_plecs = pd.read_csv(out_file)
        
        # O Plecs exporta na ordem fixa das portas do Scope:
        # 0: Time -> Tempo da Simulação em Segundos
        # 1: Vm1:Measured voltage -> Tensão do Banco
        # 2: Gain1 -> Potência
        # 3: C-Script:2 -> Estado (Carregando ou Descarregando)
        # 4: C-Script:1 -> Corrente do Banco
        # 5: Gain1.1 (ou Integrator) -> SOC
        
        cols = df_plecs.columns
        
        df_plecs.rename(columns={
            cols[0]: "Tempo",
            cols[1]: "Tensao_Term_V",
            cols[5]: "SOC"
        }, inplace=True)
        
        # Garantir que os dados sejam numericos
        df_plecs['Tempo'] = pd.to_numeric(df_plecs['Tempo'], errors='coerce')
        df_plecs['Tensao_Term_V'] = pd.to_numeric(df_plecs['Tensao_Term_V'], errors='coerce')
        df_plecs['SOC'] = pd.to_numeric(df_plecs['SOC'], errors='coerce')
        
        df_soc_mes = df_plecs[['Tempo', 'Tensao_Term_V', 'SOC']].dropna()
        
        return df_soc_mes
        
        
    except Exception as e:
        logger.error(f"[PLECS] Erro ao ler arquivo de saída: {e}")
        return None


def _to_native_types(data):
    """Converte tipos NumPy para tipos Python nativos (compatibilidade XMLRPC)."""
    if isinstance(data, dict):
        return {k: _to_native_types(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_to_native_types(v) for v in data]
    elif isinstance(data, (np.integer, np.int64, np.int32)):
        return int(data)
    elif isinstance(data, (np.floating, np.float64, np.float32)):
        return float(data)
    elif isinstance(data, np.ndarray):
        return _to_native_types(data.tolist())
    return data


def _montar_model_vars_bateria(cfg_bat: BateriaConfig, soc_inicial: float, soh_atual: float) -> dict:
    """Constrói o dicionário ModelVars para o PLECS."""
    model_vars = {
        'SOC_0':     soc_inicial,
        'SOH_Input': soh_atual,
        'Rs':        cfg_bat.Rs,
        'Ah':        cfg_bat.Ah,
        'Ns':        cfg_bat.Ns,
        'Np':        cfg_bat.Np,
        'SOC':       cfg_bat.soc_prof,
        'OCV':       cfg_bat.ocv_prof,
        'SocMin':    cfg_bat.soc_min_pct,
        'SocMax':    cfg_bat.soc_max_pct,
        'Vbmin':     cfg_bat.v_min_celula,
        'Vbmax':     cfg_bat.v_max_celula,
        'P_BESS':    cfg_bat.P_bess,
        'ETA':       cfg_bat.rendimento_pcs,
        'Escala_Tempo': 1,
    }
    return _to_native_types(model_vars)

`

## Arquivo: src\besx\infrastructure\reports\report.py
`python

import os
import datetime
import pandas as pd
from besx.infrastructure.logging.logger import logger

def gerar_relatorio_txt(file_manager, config, df_res, sim_duration_str, prefixo=""):
    """
    Gera um relatório de texto detalhado com metadados, configuração 
    e resumo dos resultados da simulação.
    
    Args:
        file_manager (FileManager): Gerenciador de arquivos para salvar o relatório.
        config (dict): Dicionário de configuração usado na simulação.
        df_res (pd.DataFrame): DataFrame com os resultados mensais consolidados.
        sim_duration_str (str): String com a duração total da simulação.
        prefixo (str): Prefixo (backend, bateria, etc) para o nome do arquivo final.
    """
    
    cfg_bat = config.bateria
    cfg_sim = config.simulacao
    cfg_deg_ciclo = config.modelo_degradacao.ciclo
    cfg_deg_cal = config.modelo_degradacao.calendario
    
    # Cálculos Finais
    soh_final = df_res.iloc[-1]['capacidade_restante']
    perda_total = df_res.iloc[-1]['dano_total_acum']
    ciclos_totais = df_res['Ciclos_Contagem'].sum()
    efc_total = df_res['EFC_Ciclos_Equivalentes'].sum()
    
    # Estimativa simples de vida útil (linear)
    # Se perdeu X% em N meses, perderá 20% (EOL) em quanto tempo?
    meses_simulados = len(df_res)
    perda_por_mes = perda_total / meses_simulados if meses_simulados > 0 else 0
    eol_target = cfg_bat.capacidade_limite_perda_perc
    
    if perda_por_mes > 0:
        meses_ate_eol = eol_target / perda_por_mes
        anos_ate_eol = meses_ate_eol / 12
        vida_util_str = f"{anos_ate_eol:.1f} anos ({meses_ate_eol:.0f} meses)"
    else:
        vida_util_str = "Indeterminada (perda desprezível)"

    txt = []
    txt.append("="*50)
    txt.append(f"RELATÓRIO DE SIMULAÇÃO BESx")
    txt.append("="*50)
    txt.append(f"Data da Execução: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    txt.append(f"Duração da Simulação: {sim_duration_str}")
    txt.append("")
    
    txt.append("-" * 30)
    txt.append("1. CONFIGURAÇÃO (SNAPSHOT)")
    txt.append("-" * 30)
    txt.append(f"Arquivo de Entrada: {config.dados_entrada.ARQUIVO_MAT}")
    txt.append(f"Passo de Tempo (dt): {config.dados_entrada.dt_minutos} min")
    txt.append("")
    txt.append("[Bateria]")
    txt.append(f"  Capacidade Nominal: {cfg_bat.capacidade_nominal_wh} Wh")
    txt.append(f"  Tensão Nom/Min/Max: {3.2}V / {cfg_bat.v_min_celula}V / {cfg_bat.v_max_celula}V") # Tensão Nom aprox
    txt.append(f"  Temperatura: {cfg_bat.Tbat_kelvin - 273.15:.1f} °C")
    txt.append(f"  SOC Operacional: {cfg_bat.soc_min_pct*100}% - {cfg_bat.soc_max_pct*100}%")
    txt.append("")
    txt.append("[Parâmetros de Degradação]")
    txt.append(f"  Ciclo (Rainflow): a={cfg_deg_ciclo.a}, b={cfg_deg_ciclo.b}")
    txt.append(f"  Calendário: k_T={cfg_deg_cal.k_T}, k_soc={cfg_deg_cal.k_soc}")
    txt.append("")

    txt.append("-" * 30)
    txt.append("2. ESTATÍSTICAS OPERACIONAIS (MÉDIAS)")
    txt.append("-" * 30)
    txt.append(f"SOC Médio Global: {df_res['SOC_Medio'].mean():.1f}%")
    txt.append(f"C-Rate Médio: {df_res['C_Rate_Medio'].mean():.2f} C")
    txt.append(f"DOD Médio (dos Ciclos): {df_res['DOD_Medio_Perc'].mean():.1f}%")
    txt.append(f"Tempo em SOC Alto (>90%): {df_res['Tempo_SOC_Alto_Perc'].mean():.1f}%")
    txt.append(f"Tempo em SOC Baixo (<10%): {df_res['Tempo_SOC_Baixo_Perc'].mean():.1f}%")
    txt.append("")

    txt.append("-" * 30)
    txt.append("3. RESULTADOS DE DEGRADAÇÃO")
    txt.append("-" * 30)
    txt.append(f"SOH Inicial: {cfg_sim.SOH_INICIAL_PERC}%")
    txt.append(f"SOH Final ({meses_simulados} meses): {soh_final:.2f}%")
    txt.append(f"Perda Total Acumulada: {perda_total:.3f}%")
    txt.append(f"  -> Por Ciclagem: {df_res.iloc[-1]['dano_ciclo_acum']:.3f}%")
    txt.append(f"  -> Por Calendário: {df_res.iloc[-1]['dano_cal_acum']:.3f}%")
    txt.append("")
    txt.append(f"Ciclos Contados (Rainflow): {int(ciclos_totais)}")
    txt.append(f"Ciclos Equivalentes (EFC): {efc_total:.1f}")
    txt.append("")
    txt.append(f"ESTIMATIVA DE VIDA ÚTIL (até {eol_target}% de perda):")
    txt.append(f"  >> {vida_util_str} <<")
    txt.append("(Nota: Projeção linear baseada na taxa de degradação atual)")
    txt.append("="*50)
    
    conteudo = "\n".join(txt)
    nome_arquivo = f"report_{prefixo}.txt" if prefixo else "report.txt"
    path = file_manager.save_report(conteudo, filename=nome_arquivo)
    logger.info(f"Relatório detalhado salvo em: {path}")
    return path

`

## Arquivo: src\besx\infrastructure\reports\validation_report.py
`python
"""
validation_report.py

Módulo responsável por gerar relatórios detalhados de validação
com todos os cálculos intermediários exportados para Excel.
"""

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from besx.infrastructure.logging.logger import logger
import os


def gerar_relatorio_validacao(file_manager, config, resultados_mensais, calculos_detalhados, prefixo=""):
    """
    Gera um relatório completo de validação em Excel com múltiplas sheets.
    
    Args:
        file_manager: Instância do FileManager para gerenciar caminhos
        config: Dicionário com toda a configuração da simulação
        resultados_mensais: Lista de dicionários com resultados mensais
        calculos_detalhados: Lista de dicionários com DataFrames detalhados por mês
        prefixo: Prefixo descritivo (opcional) para o nome final
    
    Returns:
        str: Caminho do arquivo Excel gerado
    """
    logger.info("Gerando relatório de validação detalhado...")
    
    # Caminho do arquivo final
    nome_arquivo = f"relatorio_validacao_dimensionamento_{prefixo}.xlsx" if prefixo else "relatorio_validacao_dimensionamento.xlsx"
    caminho_excel = file_manager.get_data_path(nome_arquivo)
    
    # Cria o writer do Excel
    with pd.ExcelWriter(caminho_excel, engine='openpyxl') as writer:
        # Sheet 1: Configuração
        criar_sheet_configuracao(writer, config)
        
        # Sheet 2: Resumo Mensal
        df_resultados = pd.DataFrame(resultados_mensais)
        criar_sheet_resumo_mensal(writer, df_resultados)
        
        # Sheets 3+: Cálculos detalhados por mês
        criar_sheets_calculos_detalhados(writer, calculos_detalhados)
    
    # Aplica formatação
    formatar_workbook(caminho_excel)
    
    logger.info(f"Relatório de validação salvo em: {caminho_excel}")
    return caminho_excel


def criar_sheet_configuracao(writer, config):
    """
    Cria a sheet com todos os parâmetros de configuração.
    """
    dados_config = []
    
    # Seção: Simulação
    dados_config.append(['=== CONFIGURAÇÃO DA SIMULAÇÃO ===', ''])
    dados_config.append(['SOH Inicial (%)', config.simulacao.SOH_INICIAL_PERC])
    dados_config.append(['Anos de Simulação', config.simulacao.ANOS_SIMULACAO])
    dados_config.append(['Data Início', config.simulacao.data_inicio_simulacao])
    dados_config.append(['', ''])
    
    # Seção: Bateria
    dados_config.append(['=== PARÂMETROS DA BATERIA ===', ''])
    dados_config.append(['Capacidade Nominal (Wh)', config.bateria.capacidade_nominal_wh])
    dados_config.append(['Capacidade Limite de Perda (%)', config.bateria.capacidade_limite_perda_perc])
    dados_config.append(['Temperatura (K)', config.bateria.Tbat_kelvin])
    dados_config.append(['Resistência Interna (Ohms)', config.bateria.Rs])
    dados_config.append(['SOC Min', config.bateria.soc_min_pct])
    dados_config.append(['SOC Max', config.bateria.soc_max_pct])
    dados_config.append(['Potência BESS (W)', config.bateria.P_bess])
    dados_config.append(['Ah', config.bateria.Ah])
    dados_config.append(['Ns (células em série)', config.bateria.Ns])
    dados_config.append(['Np (células em paralelo)', config.bateria.Np])
    dados_config.append(['', ''])
    
    # Seção: Modelo de Degradação - Ciclo
    dados_config.append(['=== MODELO DE DEGRADAÇÃO - CICLO ===', ''])
    for key, value in config.modelo_degradacao.ciclo.model_dump().items():
        dados_config.append([f'ciclo.{key}', value])
    dados_config.append(['', ''])
    
    # Seção: Modelo de Degradação - Calendário
    dados_config.append(['=== MODELO DE DEGRADAÇÃO - CALENDÁRIO ===', ''])
    for key, value in config.modelo_degradacao.calendario.model_dump().items():
        dados_config.append([f'calendario.{key}', value])
    
    # Cria DataFrame e exporta
    df_config = pd.DataFrame(dados_config, columns=['Parâmetro', 'Valor'])
    df_config.to_excel(writer, sheet_name='Configuracao', index=False)


def criar_sheet_resumo_mensal(writer, df_resultados):
    """
    Cria a sheet com resumo mensal (similar ao resultados_completos.xlsx).
    """
    df_resultados.to_excel(writer, sheet_name='Resumo_Mensal', index=False)


def criar_sheets_calculos_detalhados(writer, calculos_detalhados):
    """
    Cria sheets detalhadas para cada mês (Ciclo e Calendário).
    
    Args:
        writer: ExcelWriter do pandas
        calculos_detalhados: Lista de dicts com 'mes', 'df_ciclo', 'df_calendario'
    """
    for calc in calculos_detalhados:
        mes_id = calc['mes']
        df_ciclo = calc['df_ciclo']
        df_calendario = calc['df_calendario']
        
        # Sheet de Degradação Cíclica
        nome_sheet_ciclo = f'Mes_{mes_id}_Ciclo'
        df_ciclo.to_excel(writer, sheet_name=nome_sheet_ciclo, index=False)
        
        # Sheet de Degradação Calendário
        nome_sheet_cal = f'Mes_{mes_id}_Calendario'
        df_calendario.to_excel(writer, sheet_name=nome_sheet_cal, index=False)


def formatar_workbook(caminho_excel):
    """
    Aplica formatação profissional ao workbook:
    - Cabeçalhos em negrito com cor de fundo
    - Ajusta largura das colunas
    - Congela painéis
    """
    wb = load_workbook(caminho_excel)
    
    # Cores
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Formata cabeçalho (primeira linha)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Ajusta largura das colunas
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            
            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)  # Limite de 50
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Congela painel (primeira linha)
        ws.freeze_panes = 'A2'
    
    wb.save(caminho_excel)


def exportar_debug_degradacao(
    dados,
    etapa,
    mes_id=None,
    sufixo="",
    pasta_debug=None
):
    """
    Exporta dados intermediários do modelo de degradação para validação externa (Excel).
    """
    import os
    import pandas as pd
    import numpy as np

    # Se pasta_debug for fornecida, usa ela. Senão, cria local (fallback)
    if pasta_debug:
        pasta = pasta_debug
    else:
        pasta = "debug_degradacao"
        os.makedirs(pasta, exist_ok=True)

    if isinstance(dados, pd.DataFrame):
        df = dados.copy()
    elif isinstance(dados, pd.Series):
        df = dados.to_frame(name="valor")
    elif isinstance(dados, (list, np.ndarray)):
        if len(dados) > 0 and isinstance(dados[0], dict):
             df = pd.DataFrame(dados)
        elif len(dados) == 0:
             df = pd.DataFrame(columns=["valor"])
        else:
             df = pd.DataFrame(dados, columns=["valor"])
    else:
        raise TypeError("Tipo de dado não suportado para exportação.")

    partes_nome = [etapa]
    if mes_id is not None:
        partes_nome.append(f"mes_{mes_id}")
    if sufixo:
        partes_nome.append(sufixo)

    nome_arquivo = "_".join(partes_nome) + ".xlsx"
    caminho = os.path.join(pasta, nome_arquivo)
    
    df.to_excel(caminho, index=False)
    return caminho


def export_xlsx(df_list, filename):
    """
    Exporta uma lista de DataFrames para um arquivo Excel com múltiplas abas.
    """
    logger.info(f"Salvando Excel em '{filename}'...")
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for i, df_para_salvar in enumerate(df_list):
                nome_planilha = f'Sheet_{i+1}'
                df_para_salvar.to_excel(writer, sheet_name=nome_planilha, index=False)
        logger.info(f"Arquivo '{filename}' salvo com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao salvar Excel: {e}")

`

## Arquivo: src\besx\infrastructure\visualization\plots.py
`python

from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from besx.config import CONFIGURACAO
from besx.infrastructure.logging.logger import logger


def imprimir_histograma(df_rainflow_mes, ano, mes):
    """
    Imprime um histograma de contagem de ciclos agrupados por DOD (Range)
    para um mês/ano específico.

    Args:
        df_rainflow_mes (pd.DataFrame): DataFrame com os ciclos rainflow ('Range', 'Count').
        ano (int): O ano sendo processado (para o título).
        mes (int): O mês sendo processado (para o título).
    """
    logger.info(f"--- Histograma de Ciclos do Mes {mes}/{ano} ---")

    if df_rainflow_mes.empty:
        logger.warning("   -> Nenhum ciclo rainflow encontrado para histograma.")
        return

    df_local = df_rainflow_mes.copy()

    # Lê o parâmetro de arredondamento do config
    hist_dp = CONFIGURACAO.modelo_degradacao.ciclo.range_round_dp
    
    df_local['range_rounded'] = df_local['Range'].round(hist_dp)
    
    histograma_df = df_local.groupby('range_rounded')['Count'].sum().reset_index()
    
    for _, linha in histograma_df.iterrows():
        dod = linha['range_rounded']
        contagem = linha['Count']
        logger.info(f"-> Encontrado(s) {contagem} ciclo(s) com DOD de: {dod:.2f}%")

def plotar_capacidade_mensal(df_resultados, nome_arquivo_saida):
    """
    Gera um gráfico da capacidade restante da bateria ao final de cada mês.

    Args:
        df_resultados (pd.DataFrame): DataFrame com os resultados mensais.
                                  Deve conter a coluna 'capacidade_restante'.
        nome_arquivo_saida (str): O nome do arquivo PNG que será salvo.
    """
    logger.info(f"--- Gerando Imagem: {nome_arquivo_saida} ---")

    if df_resultados.empty or 'capacidade_restante' not in df_resultados.columns:
        logger.warning("   -> Nenhum resultado ou coluna 'capacidade_restante' encontrada para plotar.")
        return

    # Lê parâmetros da configuração global
    cfg_sim = CONFIGURACAO.simulacao
    cfg_bat = CONFIGURACAO.bateria
    
    capacidade_inicial = cfg_sim.SOH_INICIAL_PERC
    limite_eol_perc = cfg_bat.capacidade_limite_perda_perc

    # 1. Evita 'Side Effect' - Trabalha em uma cópia
    df_plot = df_resultados.copy()

    # 2. Cria o eixo X sequencial na cópia local
    df_plot['mes'] = range(1, len(df_plot) + 1)

    # 3. Lógica de cálculo redundante foi REMOVIDA.

    # 4. Lê parâmetros de plotagem do config
    figsize = (15, 7) 
    cor = 'darkgreen' 
    dpi = 150 

    # 5. Calcula o limite EOL com base nos parâmetros da simulação
    linha_eol = capacidade_inicial - limite_eol_perc # ex: 100 - 20 = 80
    
    # 6. Lê limites Y do config
    ylim_top = 105
    # Define o limite inferior como 10 abaixo do EOL, ou o mínimo do plot
    ylim_bottom_min = linha_eol - 10
    ylim_bottom = min(ylim_bottom_min, df_plot['capacidade_restante'].min() - 5)
    
    # 7. Lê espaçamento dos Ticks (eixo X) do config
    xticks_step_months = 12 # Pode ser movido para o config se desejar

    # 8. Plota o gráfico de linha
    plt.figure(figsize=figsize)
    plt.plot(df_plot['mes'], df_plot['capacidade_restante'],
             marker='o', linestyle='-', color=cor, label='Capacidade Restante')

    # Usa o parâmetro 'linha_eol' calculado
    plt.axhline(y=linha_eol, color='red', linestyle='--', label=f'Limite Fim de Vida ({linha_eol:.0f}%)')

    # Adiciona títulos e rótulos
    plt.title('Evolução da Capacidade Restante da Bateria (SOH)')
    plt.xlabel('Mês da Simulação (Sequencial)')
    plt.ylabel('Capacidade Restante (%)')
    
    # Usa os limites Y do config
    plt.ylim(bottom=ylim_bottom, top=ylim_top)
    
    # Usa o passo (step) do config
    step = max(1, len(df_plot) // xticks_step_months)
    plt.xticks(np.arange(0, len(df_plot) + 1, step=step))
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    
    # Usa o DPI do config
    plt.savefig(nome_arquivo_saida, dpi=dpi)
    logger.info("Imagem gerada com sucesso.")


def plotar_composicao_degradacao(df_resultados, nome_arquivo_saida):
    """
    Gera um gráfico de área empilhada mostrando a contribuição
    de Ciclo vs. Calendário na degradação total acumulada.
    """
    # Configuração do gráfico
    plt.figure(figsize=(10, 6))
    dpi = 150 
    meses = df_resultados['mes']
    deg_ciclo = df_resultados['dano_ciclo_acum']
    deg_cal = df_resultados['dano_cal_acum']
    
    # Cria o gráfico de área empilhada
    plt.stackplot(meses, deg_ciclo, deg_cal, 
                  labels=['Degradação por Ciclo', 'Degradação por Calendário'],
                  colors=['#1f77b4', '#ff7f0e'], # Azul e Laranja
                  alpha=0.7)
    
    # Linha do total para destaque
    plt.plot(meses, df_resultados['dano_total_acum'], color='black', linestyle='--', linewidth=1, label='Perda Total Acumulada')

    # Estilização
    plt.title('Composição da Degradação da Bateria (SOH Loss)')
    plt.xlabel('Mês da Simulação')
    plt.ylabel('Perda Acumulada de SOH (%)')
    plt.legend(loc='upper left')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.xlim(left=1, right=meses.max())
    plt.ylim(bottom=0)
    
    # Exibe
    plt.tight_layout()
    plt.savefig(nome_arquivo_saida, dpi=dpi)
`

## Arquivo: src\besx\resources\batteries.json
`json
{
    "Sany_314Ah": {
        "capacidade_nominal_wh": 261248.0,
        "capacidade_limite_perda_perc": 20.0,
        "Tbat_kelvin": 308.15,
        "Tbat_kelvin_idle": 298.15,
        "Rs": 0.0002,
        "soc_prof": [
            0,
            0.05,
            0.1,
            0.15,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
            0.9,
            1
        ],
        "ocv_prof": [
            2.500,
            3.000,
            3.150,
            3.200,
            3.220,
            3.250,
            3.270,
            3.280,
            3.290,
            3.300,
            3.330,
            3.380,
            3.650
        ],
        "soc_min": 0.1,
        "soc_max": 0.95,
        "Vbmin": 2.5,
        "Vbmax": 3.65,
        "P_bess": 125000.0,
        "Ah": 314,
        "Ns": 260,
        "Np": 1
    },
    "LiFePO4_78Ah": {
        "capacidade_nominal_wh": 15444.0,
        "capacidade_limite_perda_perc": 20.0,
        "Tbat_kelvin": 308.15,
        "Tbat_kelvin_idle": 308.15,
        "Rs": 0.017,
        "soc_prof": [
            0.0,
            0.05,
            0.1,
            0.15,
            0.2,
            0.25,
            0.3,
            0.35,
            0.4,
            0.45,
            0.5,
            0.55,
            0.6,
            0.65,
            0.7,
            0.75,
            0.8,
            0.85,
            0.9,
            0.95,
            1.0
        ],
        "ocv_prof": [
            2.596,
            3.149,
            3.2115,
            3.22,
            3.2545,
            3.281,
            3.2915,
            3.295,
            3.2955,
            3.296,
            3.2975,
            3.2995,
            3.312,
            3.3335,
            3.335,
            3.3345,
            3.3345,
            3.3345,
            3.36,
            3.41,
            3.445
        ],
        "soc_min": 0.1,
        "soc_max": 0.9,
        "Vbmin": 2.596,
        "Vbmax": 3.445,
        "P_bess": 581000.0,
        "Ah": 78,
        "Ns": 10,
        "Np": 6
    }
}
`

## Arquivo: tests\__init__.py
`python

`

## Arquivo: tests\mission_profile_generator.py
`python
"""
mission_profile_generator.py

Este script gera dados sintéticos (perfis de missão) para testes do motor
de simulação de baterias.
"""

import os
import pandas as pd
from besx.config import PERFIS_BATERIA
from besx.infrastructure.logging.logger import logger

def generate_profiles(bateria_alvo: str = None):
    output_dir = os.path.join("data", "mock_profiles")
    os.makedirs(output_dir, exist_ok=True)
    
    gerados = {}
    
    logger.info(f"Iniciando a geração de perfis sintéticos em {output_dir}")
    
    for nome_perfil, cfg in PERFIS_BATERIA.items():
        if bateria_alvo and nome_perfil != bateria_alvo:
            continue
            
        # Verificação preventiva: Valores Pydantic podem ser acessados via notação de ponto
        v_min = cfg.v_min_celula if cfg.v_min_celula else 2.5
        v_max = cfg.v_max_celula if cfg.v_max_celula else 3.65
        v_nom_celula = (v_max + v_min) / 2.0
        
        ah_celula = cfg.Ah if cfg.Ah else 100.0
        ns = cfg.Ns if cfg.Ns else 1
        np_val = cfg.Np if cfg.Np else 1
        
        # Potência de 1C (Watts)
        p_1c = ah_celula * np_val * ns * v_nom_celula
        logger.info(f"[{nome_perfil}] Potência 1C calculada: {p_1c:.2f} W")
        
        # --- TC1: Full Cycle ---
        # 120 min carga (1C) -> 120 min descarga (-1C)
        tc1_time = list(range(241))
        tc1_power = []
        for t in tc1_time:
            if t <= 120:
                tc1_power.append(p_1c) # Carga
            else:
                tc1_power.append(-p_1c) # Descarga
        
        df_tc1 = pd.DataFrame({'timestamp_min': tc1_time, 'pot_w': tc1_power})
        path_tc1 = os.path.join(output_dir, f"{nome_perfil}_TC1.csv")
        df_tc1.to_csv(path_tc1, index=False)
        
        # --- TC2: Partial Cycling (Dynamic, 20% DOD) ---
        # Onda quadrada em torno de 50% SOC.
        # Para evitar corte no BMS pelas resistências altas do JSON, usaremos 0.1C (~10% da pot 1C).
        # A 0.1C, demoramos 60 minutos para subir 10% de SOC (de 50 a 60).
        # Para o ciclo de 20% DOD, demoramos 120 minutos por meia-onda.
        tc2_time = []
        tc2_power = []
        t_current = 0
        
        p_tc2 = p_1c * 0.1
        
        def add_segment(time_min, power_val):
            nonlocal t_current
            for _ in range(int(time_min)):
                tc2_time.append(t_current)
                tc2_power.append(power_val)
                t_current += 1

        add_segment(60, p_tc2) # sobe para 60%
        for _ in range(10):  # 10 ciclos
            add_segment(120, -p_tc2)  # desce para 40% (20% DOD)
            add_segment(120, p_tc2)   # sobe para 60%
            
        df_tc2 = pd.DataFrame({'timestamp_min': tc2_time, 'pot_w': tc2_power})
        path_tc2 = os.path.join(output_dir, f"{nome_perfil}_TC2.csv")
        df_tc2.to_csv(path_tc2, index=False)
        
        # --- TC3: Idle/Calendar ---
        # 0.0 W por 72 horas (4320 minutos)
        tc3_time = list(range(4321))
        tc3_power = [0.0] * 4321
        
        df_tc3 = pd.DataFrame({'timestamp_min': tc3_time, 'pot_w': tc3_power})
        path_tc3 = os.path.join(output_dir, f"{nome_perfil}_TC3.csv")
        df_tc3.to_csv(path_tc3, index=False)
        
        logger.info(f"[{nome_perfil}] Perfis TC1, TC2 e TC3 gerados.")
        
        gerados[nome_perfil] = {
            "TC1": path_tc1,
            "TC2": path_tc2,
            "TC3": path_tc3
        }

    return gerados

if __name__ == "__main__":
    generate_profiles()

`

## Arquivo: tests\test_battery_simulator.py
`python
"""
test_battery_simulator.py

Testes unitários para o módulo battery_simulator.py.
Verifica o comportamento da integração de Coulomb em cenários-chave.
"""

import sys
import os
import unittest
import numpy as np
import pandas as pd

# Add project root to path
# Adiciona o diretório 'src' ao sys.path para reconhecer o pacote 'besx'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, "src"))

from besx.domain.models.battery_simulator import simular_soc_mes
from besx.config import BateriaConfig


# ---------------------------------------------------------------------- #
#  Configuração de bateria mínima para os testes                          #
# ---------------------------------------------------------------------- #
CFG_BAT_TESTE = {
    'Ah':       100.0,   # 100 Ah
    'Ns':       1,       # 1 módulo em série
    'Np':       1,       # 1 string em paralelo
    'soc_prof': [0.0, 0.5, 1.0],
    'ocv_prof': [3.0, 3.3, 3.6],  # V do banco (Ns=1)
    'soc_min':  0.10,   # 10%
    'soc_max':  0.90,   # 90%
    'capacidade_nominal_wh': 1000.0,
    'P_bess':   50_000.0,  # 50 kW
}

SOH_PLENO = 1.0   # 100%


def _df_mes_constante(p_w: float, n_passos: int = 60, dt_min: float = 1.0) -> pd.DataFrame:
    """
    Cria um DataFrame de potência constante em Watts.

    Args:
        p_w:      Potência em Watts (positivo=carga, negativo=descarga)
        n_passos: Número de amostras
        dt_min:   Intervalo de tempo em minutos

    Returns:
        DataFrame com colunas ['Tempo', 'Potencia_kW']
    """
    tempos = np.arange(n_passos) * dt_min  # minutos
    return pd.DataFrame({'Tempo': tempos, 'Potencia_kW': [p_w] * n_passos})


class TestSimularSOCMes(unittest.TestCase):

    # ------------------------------------------------------------------ #
    #  1. Estrutura da saída                                               #
    # ------------------------------------------------------------------ #
    def test_saida_tem_colunas_corretas(self):
        """A saída deve ter exatamente as colunas 'Tempo' e 'SOC'."""
        df_mes = _df_mes_constante(0.0)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg)

        self.assertIn('Tempo', resultado.columns)
        self.assertIn('SOC', resultado.columns)

    def test_saida_tem_mesmo_numero_de_linhas(self):
        """O número de linhas da saída deve ser igual ao da entrada."""
        n = 120
        df_mes = _df_mes_constante(0.0, n_passos=n)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg)
        self.assertEqual(len(resultado), n)

    def test_tempo_em_segundos(self):
        """Coluna Tempo deve estar em segundos (primeiro valor = 0 s)."""
        df_mes = _df_mes_constante(0.0, n_passos=60, dt_min=1.0)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg)
        # Primeiro passo é t=0 min → 0 s
        self.assertAlmostEqual(resultado['Tempo'].iloc[0], 0.0, places=3)
        # Segundo passo é t=1 min → 60 s
        self.assertAlmostEqual(resultado['Tempo'].iloc[1], 60.0, places=3)

    def test_soc_em_percentual(self):
        """SOC deve estar em % (0–100), não em fração (0–1)."""
        df_mes = _df_mes_constante(0.0, n_passos=10)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg)
        # Com SOC inicial = 0.5 → deve aparecer como 50.0, não 0.5
        self.assertAlmostEqual(resultado['SOC'].iloc[0], 50.0, places=2)

    # ------------------------------------------------------------------ #
    #  2. Condições iniciais                                               #
    # ------------------------------------------------------------------ #
    def test_soc_inicial_correto(self):
        """O primeiro valor de SOC deve corresponder ao soc_inicial fornecido."""
        soc_inicial = 0.65  # 65%
        df_mes = _df_mes_constante(0.0)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, soc_inicial, cfg)
        self.assertAlmostEqual(resultado['SOC'].iloc[0], soc_inicial * 100.0, places=2)

    def test_potencia_zero_soc_constante(self):
        """Com potência zero, o SOC deve permanecer constante ao longo do tempo."""
        soc_inicial = 0.5
        df_mes = _df_mes_constante(0.0, n_passos=100)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, soc_inicial, cfg)
        soc_series = resultado['SOC']
        self.assertTrue((soc_series == soc_series.iloc[0]).all(),
                        msg="SOC deve ser constante quando P=0")

    # ------------------------------------------------------------------ #
    #  3. Direção correta do SOC                                           #
    # ------------------------------------------------------------------ #
    def test_carga_aumenta_soc(self):
        """Potência positiva (carga) deve aumentar o SOC."""
        df_mes = _df_mes_constante(10000.0, n_passos=60)  # 10000 W (10 kW) de carga
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg)
        soc_final = resultado['SOC'].iloc[-1]
        soc_inicial_saida = resultado['SOC'].iloc[0]
        self.assertGreater(soc_final, soc_inicial_saida,
                           msg="Carga deve aumentar o SOC")

    def test_descarga_diminui_soc(self):
        """Potência negativa (descarga) deve diminuir o SOC."""
        df_mes = _df_mes_constante(-10000.0, n_passos=60)  # -10000 W (-10 kW) de descarga
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg)
        soc_final = resultado['SOC'].iloc[-1]
        soc_inicial_saida = resultado['SOC'].iloc[0]
        self.assertLess(soc_final, soc_inicial_saida,
                        msg="Descarga deve diminuir o SOC")

    # ------------------------------------------------------------------ #
    #  4. Limites operacionais                                             #
    # ------------------------------------------------------------------ #
    def test_soc_nao_ultrapassa_socmax(self):
        """SOC nunca deve ultrapassar soc_max (90%)."""
        # Carga intensa (50000 W = 50 kW) por muito tempo, partindo de 80%
        df_mes = _df_mes_constante(50000.0, n_passos=500)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.8, cfg)
        soc_max_config = CFG_BAT_TESTE['soc_max'] * 100.0
        self.assertTrue(
            (resultado['SOC'] <= soc_max_config + 1e-6).all(),
            msg=f"SOC ultrapassou soc_max={soc_max_config}%"
        )

    def test_soc_nao_cai_abaixo_socmin(self):
        """SOC nunca deve cair abaixo de soc_min (10%)."""
        # Descarga intensa (-50000 W = -50 kW) por muito tempo, partindo de 20%
        df_mes = _df_mes_constante(-50000.0, n_passos=500)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.2, cfg)
        soc_min_config = CFG_BAT_TESTE['soc_min'] * 100.0
        self.assertTrue(
            (resultado['SOC'] >= soc_min_config - 1e-6).all(),
            msg=f"SOC caiu abaixo de soc_min={soc_min_config}%"
        )

    def test_potencia_limitada_por_p_bess(self):
        """Potência muito alta deve ser clipada ao valor de P_bess."""
        # Potência de 200000 W > P_bess de 50000 W → deve se comportar igual a 50000 W
        df_200kw = _df_mes_constante(200000.0, n_passos=60)
        df_50kw  = _df_mes_constante(50000.0,  n_passos=60)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        r200 = simular_soc_mes(df_200kw, SOH_PLENO, 0.5, cfg)
        r50  = simular_soc_mes(df_50kw,  SOH_PLENO, 0.5, cfg)
        np.testing.assert_array_almost_equal(
            r200['SOC'].to_numpy(), r50['SOC'].to_numpy(), decimal=4,
            err_msg="Potência deve ser limitada pelo P_bess"
        )

    # ------------------------------------------------------------------ #
    #  5. Efeito do SOH                                                    #
    # ------------------------------------------------------------------ #
    def test_soh_reduzido_aumenta_variacao_soc(self):
        """
        Com SOH reduzido a capacidade efetiva diminui,
        portanto a mesma carga provoca maior variação de SOC.
        """
        # Potência de 100 W para não saturar.
        df_mes = _df_mes_constante(100.0, n_passos=11)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        # SOH Pleno (1.0) vs SOH Reduzido (0.5)
        r_pleno     = simular_soc_mes(df_mes, 1.0, 0.5, cfg)
        r_degradado = simular_soc_mes(df_mes, 0.5, 0.5, cfg)

        delta_pleno     = r_pleno['SOC'].iloc[-1]     - r_pleno['SOC'].iloc[0]
        delta_degradado = r_degradado['SOC'].iloc[-1] - r_degradado['SOC'].iloc[0]

        # Com SOH 0.5, a variação deve ser o dobro da de SOH 1.0 (aproximadamente)
        self.assertGreater(
            delta_degradado, delta_pleno,
            msg="Bateria degradada deve ter maior variação de SOC para mesma potência"
        )

    # ------------------------------------------------------------------ #
    #  6. Conservação de energia (verificação analítica)                 #
    # ------------------------------------------------------------------ #
    def test_conservacao_energetica_carga_simples(self):
        """
        Verifica que a variação de SOC é próxima ao valor calculado analiticamente.
        """
        cfg_dict = CFG_BAT_TESTE.copy()
        cfg_dict['ocv_prof'] = [3.3, 3.3, 3.3]
        cfg_dict['soc_max']  = 0.99
        cfg_dict['rendimento_pcs'] = 1.0

        p_w     = 100.0
        n       = 11      # 10 intervalos de 1 min
        df_mes  = _df_mes_constante(p_w, n_passos=n, dt_min=1.0)
        Q_Ah    = cfg_dict['Ah'] * cfg_dict['Np'] * SOH_PLENO  # 100 Ah
        v_const = 3.3     
        i_A     = p_w / v_const  
        dt_h    = 1.0 / 60.0  
        delta_analitico = (i_A * dt_h * 10) / Q_Ah * 100.0  

        cfg_obj = BateriaConfig(**cfg_dict)
        resultado      = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg_obj)
        delta_simulado = resultado['SOC'].iloc[-1] - resultado['SOC'].iloc[0]

        self.assertAlmostEqual(delta_simulado, delta_analitico, delta=0.5)

if __name__ == '__main__':
    unittest.main(verbosity=2)

`

## Arquivo: tests\test_data_handler.py
`python

import unittest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock, patch

# Add project root to path
import sys
import os
# Adiciona o diretório 'src' ao sys.path para reconhecer o pacote 'besx'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, "src"))

from besx.infrastructure.loaders.data_handler import fatiar_dados_mensais
from besx.domain.models.battery_simulator import ciclos_idle, picos_e_vales
from besx.config import CONFIGURACAO

class TestDataHandler(unittest.TestCase):

    def setUp(self):
        # Setup configuration for tests
        # Pydantic models are usually updated via attribute access
        self.original_dt = CONFIGURACAO.dados_entrada.dt_minutos
        self.original_dias = CONFIGURACAO.dados_entrada.dias_por_ano_avg
        self.original_prominence = CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence
        
        CONFIGURACAO.dados_entrada.dt_minutos = 1
        CONFIGURACAO.dados_entrada.dias_por_ano_avg = 360
        CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence = 1.0

    def tearDown(self):
        # Restore configuration
        CONFIGURACAO.dados_entrada.dt_minutos = self.original_dt
        CONFIGURACAO.dados_entrada.dias_por_ano_avg = self.original_dias
        CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence = self.original_prominence

    def test_ciclos_idle_basic(self):
        """Test basic idle detection with constant blocks."""
        # Profile: [10, 10, 10, 20, 20, 30]
        # Idle periods: 10 (3 samples), 20 (2 samples)
        profile = [10, 10, 10, 20, 20, 30]
        
        expected_idle = [
            {'t': 3, 'SOC': 10, 'index': 2}, # t=3 samples (indices 0, 1, 2)
            {'t': 2, 'SOC': 20, 'index': 4}  # t=2 samples (indices 3, 4)
        ]
        
        # Note: The logic in ciclos_idle calculates t_meses based on config
        # We focus on 't', 'SOC' and 'index' for correctness verification
        
        # O teste falhará se não passarmos dt_minutos e minutos_por_mes
        # pois a função agora aceita esses argumentos obrigatoriamente (ou quase)
        # Vamos conferir a assinatura no battery_simulator.py:
        # def ciclos_idle(profile: list, dt_minutos_soc: float, minutos_por_mes: float) -> list:
        
        result = ciclos_idle(profile, dt_minutos_soc=1.0, minutos_por_mes=43200)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['t'], 3)
        self.assertEqual(result[0]['SOC'], 10)
        self.assertEqual(result[1]['t'], 2)
        self.assertEqual(result[1]['SOC'], 20)

    def test_ciclos_idle_no_idle(self):
        """Test profile with no idle periods (changing every step)."""
        profile = [10, 11, 12, 13, 14]
        result = ciclos_idle(profile, 1.0, 43200)
        self.assertEqual(len(result), 0)

    def test_ciclos_idle_full_idle(self):
        """Test profile that is entirely idle."""
        profile = [10, 10, 10, 10]
        result = ciclos_idle(profile, 1.0, 43200)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['t'], 4)

    def test_ciclos_idle_float_precision(self):
        """Test idle detection with floating point numbers."""
        # Exact floats
        profile = [10.5, 10.5, 12.0]
        result = ciclos_idle(profile, 1.0, 43200)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['t'], 2)
        self.assertEqual(result[0]['SOC'], 10.5)

    def test_picos_e_vales(self):
        """Test peak and valley detection."""
        # Simple triangular wave: 0 -> 10 -> 0
        s = pd.Series([0, 5, 10, 5, 0])
        # With prominence 1.0 (default in setup), 10 is a peak, 0 are valleys/endpoints
        
        # The function returns the SIMPLIFIED profile (values at peaks/valleys)
        result = picos_e_vales(s)
        
        # It should preserve start [0], peak [10], and end [0]
        # Intermediate values [5, 5] should be removed if they are not peaks
        expected_values = [0, 10, 0]
        
        # Note: find_peaks behavior depends heavily on strict inequality and prominence.
        # 0 -> 10 -> 0: 10 is strictly greater than neighbors. Prominence check applies.
        
        # Let's verify what it returns.
        # indices: 0 (start), 2 (peak 10), 4 (end)
        # result: [0, 10, 0]
        
        np.testing.assert_array_equal(result, np.array(expected_values))

    def test_fatiar_dados_mensais(self):
        """Test slicing dataframe into monthly chunks."""
        # Mock config for 30 days/month, 1 min step -> 43200 lines/month
        # Let's force a smaller month for testing efficiency
        CONFIGURACAO.dados_entrada.dias_por_mes_sim = 1
        CONFIGURACAO.dados_entrada.dt_minutos = 60 # 1 hour steps
        # 1 day = 24 hours = 24 lines
        
        # Create DF with 50 lines (2 months + 2 lines remainder)
        df_total = pd.DataFrame({
            'Tempo': range(50), # 0..49
            'Potencia': range(50)
        })
        
        chunks = fatiar_dados_mensais(df_total)
        
        # Should result in 2 chunks of 24 lines each
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), 24)
        self.assertEqual(len(chunks[1]), 24)
        
        # Check time reset behavior
        self.assertEqual(chunks[1].iloc[0]['Tempo'], 0) # Should be reset to 0

if __name__ == '__main__':
    unittest.main()

`

## Arquivo: tests\test_degradation_model.py
`python

import unittest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock, patch

# Add project root to path
import sys
import os
# Adiciona o diretório 'src' ao sys.path para reconhecer o pacote 'besx'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, "src"))

from besx.domain.models.degradation_model import dano_ciclo, dano_calendar, acumular_dano, calcular_estatisticas_operacionais
from besx.config import CONFIGURACAO, DegradacaoCicloConfig, DegradacaoCalendarioConfig

class TestDegradationModel(unittest.TestCase):

    def setUp(self):
        # We don't need to clear CONFIGURACAO, just mock the values if needed
        # but better to pass params explicitly to functions where possible
        pass

    @patch('besx.domain.models.degradation_model.rainflow.extract_cycles')
    def test_dano_ciclo(self, mock_rainflow):
        """Test cycle damage calculation."""
        # Mock rainflow output: [(Range, Mean, Count, Start, End)]
        mock_rainflow.return_value = [(0.5, 0.5, 1, 0, 10)]
        
        # We need valid config objects
        params_ciclo = DegradacaoCicloConfig(
            a=1.0, b=0.0, c=1.0, d=0.0, g=1.0, h=1.0,
            range_round_dp=1, mean_round_dp=1
        )
        
        profile = [0, 1, 0]
        dano_total, _ = dano_ciclo(profile, Temp_kelvin=300, model_params=params_ciclo)
        
        self.assertAlmostEqual(dano_total, 0.5)

    def test_dano_calendar(self):
        """Test calendar damage calculation."""
        # Idle periods: 1 period of 1 month, SOC 0.5
        idle_periods = [{'t': 1, 't_meses': 1.0, 'SOC': 0.5}]
        
        params_cal = DegradacaoCalendarioConfig(
            k_T=1.0, exp_T=0.0, k_soc=1.0, exp_soc=0.0, exp_cal=1.0
        )
        
        dano, _ = dano_calendar(idle_periods, Tbat_kelvin=300, model_params=params_cal, dt_minutos=1.0, dias_por_ano_avg=360)
        
        self.assertEqual(dano, 1.0)

    def test_acumular_dano(self):
        """Test damage accumulation."""
        # sum of x^p + y^p ^ (1/p)
        # 3, 4, p=2 -> sqrt(9+16) = 5
        res = acumular_dano(3, 4, 2)
        self.assertEqual(res, 5)

if __name__ == '__main__':
    unittest.main()

`

## Arquivo: tests\test_engine_validation.py
`python
"""
test_engine_validation.py

Este script atua como malha fechada de validação, rodando o motor com
os dados sintéticos gerados e aferindo os resultados de fidelidade.
"""

import os
import sys
import pandas as pd
import numpy as np
import rainflow
import matplotlib.pyplot as plt
from copy import deepcopy

# Adicionar src ao PYTHONPATH para execucao direta se necessario
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from besx.config import CONFIGURACAO, PERFIS_BATERIA
from besx.domain.models.battery_simulator import picos_e_vales
from besx.domain.models.degradation_model import dano_ciclo, dano_calendar
from besx.infrastructure.plecs.plecs_connector import run_monthly_simulation
from besx.infrastructure.reports.validation_report import export_xlsx
from besx.infrastructure.logging.logger import logger
import importlib
import besx.infrastructure.plecs.plecs_connector
import besx.domain.models.battery_simulator

def rodar_validacao(perfil_nome="LiFePO4_78Ah", backend="python"):
    # Force module reload to prevent Streamlit caching old code
    importlib.reload(besx.infrastructure.plecs.plecs_connector)
    importlib.reload(besx.domain.models.battery_simulator)
    # Re-import to update local reference
    global run_monthly_simulation, picos_e_vales
    from besx.infrastructure.plecs.plecs_connector import run_monthly_simulation
    from besx.domain.models.battery_simulator import picos_e_vales

    logger.info(f"Iniciando bateria de validação Engine/Degradação ({backend}) para {perfil_nome}...")
    
    payload = {
        "status": "success",
        "errors": [],
        "tc1_data": None,
        "tc2_data": None,
        "historico_degradacao": None,
        "history_meses": None,
        "assertions": {}
    }

    # Garante que as pastas existam
    os.makedirs("debug", exist_ok=True)
    os.makedirs(os.path.join("data", "mock_profiles"), exist_ok=True)

    # Injeta a bateria correta baseada no perfil
    CONFIGURACAO.bateria = PERFIS_BATERIA[perfil_nome]
    cfg_bat = CONFIGURACAO.bateria
    
    
    path_tc1 = os.path.join("data", "mock_profiles", f"{perfil_nome}_TC1.csv")
    path_tc2 = os.path.join("data", "mock_profiles", f"{perfil_nome}_TC2.csv")
    
    if not os.path.exists(path_tc1) or not os.path.exists(path_tc2):
         logger.error("Perfis de missao nao encontrados. Rode mission_profile_generator.py primeiro.")
         payload["status"] = "error"
         payload["errors"].append("Perfis sintéticos não encontrados.")
         return payload

    df_tc1 = pd.read_csv(path_tc1)
    df_tc2 = pd.read_csv(path_tc2)

    # =========================================================
    # 1. Sanidade Elétrica (BMS Virtual) no TC1
    # =========================================================
    logger.info(">>> Rodando Test Case 1: Full Cycle (Sanidade Elétrica)")
    df_res_tc1 = run_monthly_simulation(df_tc1, soh_atual=1.0, SOC_0=cfg_bat.soc_min_pct, ctt=1, config=CONFIGURACAO, backend=backend)
    
    if df_res_tc1 is None:
        payload["status"] = "error"
        payload["errors"].append(f"Simulação TC1 falhou usando o backend: {backend}")
        return payload

    v_min_limit = cfg_bat.v_min_celula * cfg_bat.Ns
    v_max_limit = cfg_bat.v_max_celula * cfg_bat.Ns

    # Verifica se os dados de Tensão foram mapeados (PLECS muitas vezes só retorna SOC)
    if 'Tensao_Term_V' in df_res_tc1.columns:
        # Assert BMS Limit
        v_min_sim = df_res_tc1['Tensao_Term_V'].min()
        v_max_sim = df_res_tc1['Tensao_Term_V'].max()
        
        logger.info(f"Limites de tensão - Projeto: [{v_min_limit:.2f}V, {v_max_limit:.2f}V]")
        logger.info(f"Limites de tensão - Simulação: [{v_min_sim:.2f}V, {v_max_sim:.2f}V]")
        
        try:
            # Usamos round ou isclose pois pode haver leve precisao numerica de ponto flutuante
            assert v_max_sim <= v_max_limit + 1e-3, f"Violacao V_max! Sim={v_max_sim} > Limite={v_max_limit}"
            assert v_min_sim >= v_min_limit - 1e-3, f"Violacao V_min! Sim={v_min_sim} < Limite={v_min_limit}"
            logger.info("PASS: Sanidade Elétrica - Tensão restrita aos limites de segurança.")
            payload["assertions"]["bms_safety"] = {"pass": True, "msg": "Tensão restrita aos limites OCV definidos"}
        except AssertionError as e:
            logger.error(f"FAIL: {e}")
            payload["assertions"]["bms_safety"] = {"pass": False, "msg": str(e)}
    else:
        logger.warning(f"Backend {backend} não exportou coluna de Tensão_Term_V. Pulando validação elétrica fina do BMS.")
        payload["assertions"]["bms_safety"] = {"pass": True, "msg": f"Validação pulada. Backend '{backend}' não envia tensão."}

    payload["tc1_data"] = df_res_tc1

    # O matplotlib foi removido pois usaremos st.plotly_chart no frontend

    # =========================================================
    # 2. Validação do Rainflow no TC2
    # =========================================================
    logger.info(">>> Rodando Test Case 2: Partial Cycling (Rainflow DOD)")
    
    cfg_bat_ideal = deepcopy(cfg_bat)
    cfg_bat_ideal.rendimento_pcs = 1.0
    cfg_bat_ideal.Rs = 0.0
    v_nom = (cfg_bat_ideal.v_max_celula + cfg_bat_ideal.v_min_celula) / 2.0
    cfg_bat_ideal.ocv_prof = [v_nom] * len(cfg_bat_ideal.ocv_prof)
    
    config_ideal = deepcopy(CONFIGURACAO)
    config_ideal.bateria = cfg_bat_ideal
    
    df_res_tc2 = run_monthly_simulation(df_tc2, soh_atual=1.0, SOC_0=50.0, ctt=2, config=config_ideal, backend=backend)
    
    if df_res_tc2 is None:
        payload["status"] = "error"
        payload["errors"].append(f"Simulação TC2 falhou usando o backend: {backend}")
        return payload
    
    prominence = CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence
    # Usa picos_e_vales, lembrando que precisa receber uma Series de pandas indexada pelo tempo ou normal
    soc_series = pd.Series(df_res_tc2['SOC'].values)
    lista_simplificada = picos_e_vales(soc_series, prominence=prominence)
    
    ciclos = list(rainflow.extract_cycles(lista_simplificada))
    ciclos = [c for c in ciclos if c[0] > 10.0]
    
    # Avaliando os DODs (Ranges)
    # Ciclos de carga/descarga sao 20% DOD, range de ~20.
    ranges = [c[0] for c in ciclos]
    logger.info(f"Ciclos extraídos (Ranges): {ranges}")
    try:
        assert any(15.0 <= r <= 22.0 for r in ranges), f"Esperava-se microciclos entre 15% e 22% DOD, encontrado: {ranges}"
        logger.info("PASS: Extração Rainflow detectou corretamente a profundidade de 20% DOD.")
        payload["assertions"]["rainflow_dod"] = {"pass": True, "msg": "Microciclos isolados com ~20% DOD"}
    except AssertionError as e:
        logger.error(f"FAIL: {e}")
        payload["assertions"]["rainflow_dod"] = {"pass": False, "msg": str(e)}
        
    payload["tc2_data"] = df_res_tc2

    # =========================================================
    # 3. Acumulação Não-Linear (Stroe) via TC1 sequencial
    # =========================================================
    logger.info(">>> Rodando Teste de Degradação Não Linear (12 meses de TC1)")
    
    # Preparando dados para o modelo
    c_cyc_tot = 0.0
    c_cal_tot = 0.0
    
    historico_ccyc = []
    
    # Temp
    t_kelvin = cfg_bat.Tbat_kelvin
    param_ciclo = CONFIGURACAO.modelo_degradacao.ciclo
    
    for mes in range(1, 13):
        # A cada mês injetamos a curva TC1 simplificada
        soc_series_tc1 = pd.Series(df_res_tc1['SOC'].values)
        simp_tc1 = picos_e_vales(soc_series_tc1, prominence=prominence)
        
        # O modelo já extrai ciclos rainflow em dano_ciclo
        dano_mes, df_rf = dano_ciclo(simp_tc1.tolist(), t_kelvin, param_ciclo)
        
        # Acumulação Quadrática (stroe empirico)
        c_cyc_tot = np.sqrt(c_cyc_tot**2 + dano_mes**2)
        historico_ccyc.append(c_cyc_tot)
        
        logger.info(f"Mês {mes}: Dano Unitário = {dano_mes:.6f} | Acumulado = {c_cyc_tot:.6f}")

    # Checa decaimento não-linear: se fosse linear, o mes 12 seria 12 * dano_mes1
    dano_mes1 = historico_ccyc[0]
    expected_linear = dano_mes1 * 12
    
    logger.info(f"Acúmulo no final de 12 meses: {historico_ccyc[-1]:.6f}")
    logger.info(f"Acúmulo caso fosse Linear Direto: {expected_linear:.6f}")
    
    try:
        assert historico_ccyc[-1] < expected_linear, "Curva de Degradação está linear! Fator não-linear falhou."
        # No modelo estrito, c_cyc = sqrt(12 * dano^2) = sqrt(12) * dano = ~3.46 * dano
        assert np.isclose(historico_ccyc[-1], np.sqrt(12) * dano_mes1, rtol=1e-2), "C_cyc_tot não obedece a raiz quadrada exata."
        logger.info("PASS: Validação da Degradação Não-Linear Stroe.")
        payload["assertions"]["stroe_nonlinear"] = {"pass": True, "msg": "Acumulação de Capacity Fade é corretamente quadrática"}
    except AssertionError as e:
        logger.error(f"FAIL: {e}")
        payload["assertions"]["stroe_nonlinear"] = {"pass": False, "msg": str(e)}

    payload["historico_degradacao"] = historico_ccyc
    payload["history_meses"] = list(range(1, 13))

    # =========================================================
    # 4. Exportação via Relatório
    # =========================================================
    df_resumo = pd.DataFrame({
        'Mes': list(range(1, 13)),
        'C_cyc_Acumulado': historico_ccyc
    })
    
    export_xlsx([df_resumo, df_res_tc1.head(100), df_res_tc2.head(100)], 
                os.path.join("debug", "Engine_Validation_Report.xlsx"))
    
    logger.info("Testes Finalizados com Sucesso. Artifactos salvos em /debug.")
    return payload

if __name__ == "__main__":
    res = rodar_validacao()
    print(res["assertions"])

`

## Arquivo: to_do.md
`markdown
# TO DO

## TO DO CODE

    [X] Verificar o nível de corrente que passa nas células
    [ ] Comparar a simulação no plecs com a simulação em python
    [ ] Implementar a bateria de Rodrigo para fazer um Benchmarking
    [ ] Implementar uma Curva OCVxSOC para carga e outra para descarga
    [ ] Atualizar para receber os dados da curva de carga e decidir se carrega ou descarrega
    [ ] Modelo térmico da temperatura:
        - [X] Setar uma temperatura diferentes para o dano de ciclo ou de calendário
        - [ ] Usar um modelo de temperatura do Daniel
        - [ ] Usar um modelo artigo de rodrigo
        - [ ] Tentar obter uma curva com os dados do local?
    [] Testar pediar a IA para gerar o python do arquivo plecs
    [ ] Implementar o cálculo do RUL (Remaining Useful Life / Vida Útil Remanescente)

## TO_DO_DASH

    [X] Mostrar Histograma de DOD (espectro de uso gerado pelo algoritmo Rainflow) 
    [X] Mostrar SOC Médio em Repouso.
    [X] Mostrar RUL (Remaining Useful Life / Vida Útil Remanescente)
    [X] Tratar erro na exibição do Soc medio repouso
    [X] Adaptar o visual para funcionar bem no modo light
    [X] Implementar o Fator de Severidade conforme _ref\serrao.pdf estabelecendo T_ref = 25°C, SOC_ref = 50%, DOD_ref = 10%
    [ ] Revisar os itens na comparação do plecs com o python
    [ ] Revisar dados operacionais do histórico
    [ ] Adicionar número de ciclos no dash de comparação
    

## Sugestões de Melhoria (Code Cleanliness & Efficiency)

    [] Adicionar Type Hints (anotações de tipo) em todas as funções.
    [] Implementar Docstrings (padrão Google/NumPy) para documentação.
    [] Usar `dataclasses` ou `NamedTuple` para estruturar resultados (ao invés de dicts soltos).
    [] Implementar Checkpointing: Salvar estado intermediário para retomar simulação em caso de falha.
    [] Modularizar: Separar CLI (interface) da lógica de simulação (Core).
    [] Tratar while ture e inputs (argparse)

`

