# Автоматизированная оценка качества города по открытым данным
## Композитный индекс
**Urban Quality Index (UQI)** - *композитный* индекс качества городской среды, особенностью которого является:
* Учет объективных параметров города и субъективного восприятия этих параметров людьми (то есть учет объективно-субъективной природы качества города)
* Автоматизированный численный расчет
* Использование открытых данных
* Крупный масштаб (оценка агрегируется и усредняется в пределах h3-ячеек, то есть в масштабе квартала)

UQI представляет собой сумму двух индикаторов: **объективного** и **субъективного**:

$$UQI = Obj + Subj,$$

Объективный индикатор $Obj$ есть сумма показателей, характеризующих инфраструктуру, а субъективный $Subj$ – показатель социального резонанса (риск).

Индекс UQI агрегируется и усредняется в пределах h3-ячеек, с параметром `resolution` равным 8, что соответствует концепции 15-ти минутного города.

> Алгоритм разработан в рамках ВКР "Проектирование и разработка сервиса оценки городских зон на основе открытых данных".

## Объективный индикатор
### Доступность
**Доступность (accessibility)** – это оценка легкости, с которой люди могут получить доступ к различным к различным ресурсам, услугам и возможностям (к различным удобствам в широком смысле слова). Доступность показывает, до каких объектов социальной и транспортной инфраструктуры можно добраться в пределах требуемого времени.

$$𝐴_{𝑖𝑚}=\sum_{𝑛=1}^𝑁𝑓(𝐷_{𝑖𝑛𝑚}),$$

где $A_{im}$ - коэффициент доступности для i-го узла при использовании режима передвижения; $f(D_{inm})$ -  функция затухания на перемещение из i-го узла в n при использовании режима передвижения m.

### Близость
**Близость (proximity)** показывает, какое минимальное расстояние требуется преодолеть, чтобы достичь какого-либо POIs (например, школы).

$$\begin{equation} P_{im} = \begin{cases} \min_{1<n<N}(D_{in}), D_{in} \leq T \\ T, D_{in} > T  \end{cases}, \end{equation}$$

где $D_{in}$ - расстояние между узлами i и n; $T$ - пороговое значение расстояния, в пределах которого рассчитывается близость.

> Доступность и близость характеризуют социальную и транспортную инфраструктуру.

## Субъективный индикатор
### Риск
Субъективная оценка выражается численно с помощью метрики риска событий, выявленных по сообщениям из социальных сетей.

$$Risk = idw,$$
где i – интенсивность (количество отдельных текстов на событие); d – продолжительность (количество дней, когда событие было активным); w – значимость (среднее значение негатива в текстах по городским функциям, рассчитанное методами анализа настроений).

> Риск события характеризует степень воздействия события на жителей.

# Схема алгоритма
![uqi_scheme](/images/uqi_scheme_presentation_wbg_300.png)

## Используемые технологии
* [Pyrosm](https://github.com/HTenkanen/pyrosm) (выгрузка данных для объективного индикатора из OpenStreetMap)
* [Pandana](https://github.com/UDST/pandana) (автоматический расчет доступности и близости для объективного индикатора)
* [SOIKA](https://github.com/iduprojects/SOIKA) (автоматическая обработка текста, выделение событий, расчет риска для субъективного индикатора)
* [H3-pandas](https://github.com/DahnJ/H3-Pandas) (агрегация и усреднение оценки в гексагональные ячейки системы H3)

## Статьи 
1. Брюшинин А.А., Войтюк Т.Е. (науч. рук. Войтюк Т.Е.) Автоматизированная оценка качества городских зон по открытым данным // Сборник тезисов докладов конгресса молодых ученых. Электронное издание. – СПб: Университет ИТМО, [2024]. URL: https://kmu.itmo.ru/digests/article/13033

