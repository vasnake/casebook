# -*- mode: text; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

################################################################################

Письмо 1

Есть некая система – http://casebook.ru
Там содержится информация по всяким юридическим делам.
Мы можем раз в день читать автоматом оттуда данные и складывать в базу?

################################################################################

Письмо 2

Примерный сценарий пользователя на сайте
Со слов адвоката, типичный запрос выглядит так…
Вводим в поле Поиск название организации,
выбираем дело
и переходим к кому-то из участников.
Тут нужны все поля. Потестироваться можно на названии и реквизитах – ИНН, КПП и пр. ОГРН.
Отсюда почти всегда качают выписку из ЕГРЮЛ (ссылка в левом верхнем углу) и очень часто
используется кнопка Запрос данных (в разделе История изменений руководителя),
но после нажатия кнопки всплывает оповещение «Документация будет подготовлена в течение 15 минут. О готовности мы сообщим по электронной почте.», через некоторое время в почту падает не оповещение, а ответ примерно такого вида:
...
Дальше остальные пункты верхнего меню:
Отчётность (нужна реже, но целиком),
Арбитражные дела и
Дела СОЮ (как правило дальнейший поиск по участникам как уже описанный).

################################################################################

Письмо 3

Заходим в Casebook под имеющейся учёткой, в поле Поиск вводим газпром,
в предложенном списке вариантов дважды
кликаем на
OAO «ГАЗПРОМБАНК»
видим выдачу из 66 строк. Это остальные участники всех судебных процессов с участием OAO «ГАЗПРОМБАНК».
Можно ткнуть в название участника и получить по нему судебную статистику,
можно в любой другой столбец в строке – прямо в списке раскроется карточка участника со списком дел.
В верхнем меню кликаем Арбитражные дела – видим список соответствующих дел с участием нашего фигуранта.
Аналогично Дела СОЮ – дела судов общей юрисдикции.
По клику на номере дела откроется описание дела с возможностью скачать документы по делу, находящиеся в общем доступе.
В списке Участники ниже поля Поиск можем уточнить – ищем ли мы все дела с участием OAO «ГАЗПРОМБАНК»,
или только где он выступает в конкретной роли (истец, ответчик и т.п.).
Кликом по любой фамилии (ИНН, названию организации и т.п.), являющейся ссылкой, можно получить информацию по соответствующему персонажу и т.п.
В качестве затравки для поиска можно использовать название любой известной компании или банка, любую распространённую фамилию.
В выдаче по ним можно взять для примера номера дел.
Наши юристы чаще всего ищут документы (решения и определения судов) и информацию о сроках заседаний, обжалований, ушло ли дело на апелляцию и т.п.

################################################################################

Письмо 4

Задача - исходя из поиска по заданным параметрам собрать ВСЮ имеющуюся в Кейсбуке информацию.

1.       Поиск по делам:
Как пример, интересны следующие дела:
    - № А40-51217/2011
    - № А65-27211/2011
    - № А40-27010/2012

2.       Поиск по лицам:
    а) по юридическим лицам (компаниям)
    - ОАО «ЛУКОЙЛ-Коми» (ИНН 1106014140 )
    - компания «Демесне Инвестментс Лимитед»
(здесь возникает один интересный вопрос; дело в том, что у иностранных компаний нет ни ИНН, ни ОГРН; можно попробовать в таких случаях помимо наименования добавлять адрес, но не уверен, что это может помочь; в общем, написал Вам иностранную компанию в качестве «интересного случая» для проверки правильности работы программы; посмотрите как программа будет работать с такими запросами и тогда сможем понимать как с этим жить (мое скромное мнение)(или же давайте как-то это обсудим));
    - ОАО «Глобинторг» (ИНН 7723830905)

    б) по физическим лицам
    - Волков Валерий Юрьевич
    - Габдрахимов Александр Мухаматшевич
    - Шейдорова Александра Витальевна

################################################################################

Поисковые запросы и результаты, обзор исследования работы casebook.ru

При нажатии кнопки "Искать" поиск проводится тремя запросами к сайту: suggest, cases, sides.
Запросы выдаются одновременно и отображение начинается после отработки последнего.
suggest нужен только для подсказок в поле ввода.
Реально поиск проводится по cases, sides. (http://casebook.ru/api/Search/Cases, http://casebook.ru/api/Search/Sides)
Выдача результата в браузер идет в зависимости от того, что найдено - если дел не найдено, выводятся стороны.

Результаты выдаются браузеру в виде иерархических объектов в виде текста JSON.
Объекты могут различаться по составу, но часто можно выделить общие свойства.
Если свойство присутствует, его значение может быть как пустой строкой, так и null, помимо ожидаемого значения.
Браузер с помощью JavaScript разбирает ответ и формирует UI.

Итак, в качестве результатов поиска по двум службам (sides, cases) мы получаем (вынесем разные ошибки за скобки) две коллекции:
 - список сторон (sides)
 - список дел (cases)

- Рассмотрим стороны (sides)

Каждая сторона (участник) характеризуется такими основными параметрами (подробный разбор см.ниже):
    название
    ИНН, ОГРН, ОКПО
    адрес
    ФИО начальника
    признак физ.лица

Тут все очень просто. Проблемы приходят, когда начинается рассмотрение дел (cases).

- Рассмотрим дела (cases)

Каждое дело характеризуется такими основными параметрами (подробный разбор см.ниже):
    номер
    дата
    судья
    суд
    разный описательный текст
    тип дела
    сумма денег
    список инстанций (судов)
    список сторон (участников)
    последнее событие (или список последних событий)
    следующее (ожидаемое) событие

Тут (особенно в списках) выделяются связанные с "делом" сущности: инстанция (суд), судья, сторона (участник), событие, физ.лицо

Инстанция:
    название инстанции
    суд
    судья
    уровень инстанции
    даты входа-выхода дела

Участник:
    тип
    название
    ИНН, ОГРН, ОКПО
    адрес
    ФИО начальника
    признак физ.лица

Событие:
    дата
    описание
    суть события (список вопросов)
    тип события
    ссылка на документ
    суд
    судья
    номер инстанции?
    заявитель

Итого, можно выделить такие сущности:
    дело
    инстанция
    суд
    судья
    сторона (участник)
    физ.лицо (в том числе как сторона и как начальник и как самостоятельное физ.лицо)
    событие
    документ

Между собой эти сущности могут быть связаны:
    дело проходит по разным инстанциям
    в деле участвуют разные стороны
    сторона в разных делах может быть разных типов (истец, ответчик, ...)
    по делу происходят разные события
    дело рассматривается судьей, в суде
    в инстанции дело рассматривается судьей, в суде
    у участника может быть начальник - физ.лицо
    по событию может быть документ
    событие назначено в инстанцию
    событие разбирается в суде, судьей
    событие подано заявителем - участником

################################################################################

Поиск дел - POST http://casebook.ru/api/Search/Cases

Тело запроса "payload" передается в виде текста JSON -
{"StatusEx":[],"SideTypes":[],"ConsiderType":-1,"CourtType":-1,"CaseNumber":null,"CaseCategoryId":"","MonitoredStatus":-1,"Courts":[],"Instances":[],"Judges":[],"Delegate":"","StateOrganizations":[],"DateFrom":null,"DateTo":null,"SessionFrom":null,"SessionTo":null,"FinalDocFrom":null,"FinalDocTo":null,"MinSum":0,"MaxSum":-1,"Sides":[],"CoSides":[],"Accuracy":2,"Page":1,"Count":30,"OrderBy":"incoming_date_ts desc","JudgesNames":[],"Query":"№ А40-51217/2011"}
В котором главынй параметр поиска - "Query":"№ А40-51217/2011"

Ответ приходит как обьект JSON
{
  "Message": "",
  "ServerDate": "2014-03-21T13:59:41.0008466+04:00",
  "Success": true,
  "Page": 1,
  "PageSize": 30,
  "TotalCount": 1,
  "PagesCount": 1,
  "Timings": [
    "GetCasesIdsFormSpx 00:00:00.6140000",
    "GetCasesList.Sql 00:00:00.2880000",
    "GetCaseBankruptStages 00:00:00.0400000",
    "GetCasesList.SortAndMerge 00:00:00",
    "Warnings:"
  ]
  "Result": {объект развернут ниже}
}

Забегая вперед, можно отметить, что в браузере показываются следующие параметры дел:
Дело
    resp.Result.Items[i].CaseNumber - официальный номер дела
    resp.Result.Items[i].StartDate - начальная дата рассмотрения дела? Юристы знают
Текущая инстанция
    resp.Result.Items[i].Instances[j].Judge - фамилия И.О. судьи
    resp.Result.Items[i].Instances[j].Court - название суда
Участники (первый - ответчик)
    resp.Result.Items[i].BankruptStage - что-то из юр.терминологии про судопроизводство. Пока попадалось только "Конкурсное производство". Юристы знают.
    resp.Result.Items[i].Sides[j].Type - число, тип стороны (1 - ответчик, 0 - истец, и т.д.). Этот параметр отсутствует в оригинальном описании стороны (привносится из дела)
    resp.Result.Items[i].Sides[j].Name - название стороны
Последнее событие/Будущее событие
    resp.Result.Items[i].LastEvents[j].Date - дата события
    resp.Result.Items[i].LastEvents[j].Court - название суда
    resp.Result.Items[i].LastEvents[j].ContentTypes - список вопросов, повестка заседания?

В JSON ответе нужно поинтересоваться следующими параметрами:
resp.Success - if false - error, что значит - сбой авторизации, сервера или еще чего. Сообщение о неприятностях надо брать в
resp.Message - если все в порядке, то сообщение пустое. Если сообщение есть, то была ошибка или есть предупреждение
    в любом случае непустого сообщения, данные результата недостоверны.
resp.TotalCount - число найденных по запросу дел.
resp.Timings - может быть null или массив строк, применяется при отладке и содержит значения задержек или сообщения о обломе отдельных агентов.
resp.Result - обьект с данными ответа, может быть пустой (в примере обьект содержит одно найденное дело):

  "Result": {
    "MaxSum": -1.0,
    "FoundSideIdByCaseId": {
      "6a85b808-24f6-4ddb-ae53-60ffde4cbca0": 1878762
    },
    "Items": [массив развернут ниже]
  }

В данных содержится такая информация:
resp.Result.FoundSideIdByCaseId - словарь (список имя-значение), может быть пустой.
    Имя это CaseId, идентификатор дела; значение это FakeId в списке сторон Sides.
    Зачем это нужно - пока не ясно, ибо по каждому делу сторон много, тогда как в этом списке - одна сторона на одно дело.
resp.Items - список найденных дел, может быть пустой:

    "Items": [
      {
        "CaseId": "6a85b808-24f6-4ddb-ae53-60ffde4cbca0",
        "FoundInstanceId": "00000000-0000-0000-0000-000000000000",
        "CaseNumber": "А40-51217/2011",
        "StartDate": "2011-08-30T00:00:00",
        "JudgeId": "4ff54bc1-4f40-426a-aa70-63c1fdf5e0a9",
        "Judge": "Сабирова М. Ф.",
        "Court": "АС города Москвы",
        "BankruptStage": "Конкурсное производство",
        "Status": "Рассматривается в апелляционной, первой, надзорной и кассационной инстанциях",
        "CaseTypeMCode": "Б",
        "CaseCategory": "О несостоятельности (банкротстве)",
        "CaseType": "о несостоятельности (банкротстве) организаций и граждан",
        "ClaimSum": 16355838800.99,
        "RecoverySum": 16355838800.99,
        "Comment": "",
        "IsMonitored": false,
        "InFolders": [],
        "IsFavorite": false,
        "UpdatesCount": 0,
        "IsGJ": false,
        "IsSimpleJustice": false,
        "Instances": [see explanation later],
        "Sides": [see explanation later],
        "LastEvents": [see explanation later],
        "NextEvent": {see explanation later}
      }
    ]

Внутри каждого найденного дела могут быть интересны следующие данные:
resp.Result.Items[i].CaseId - системный идентификатор дела
resp.Result.Items[i].CaseNumber - официальный номер дела
resp.Result.Items[i].StartDate - начальная дата рассмотрения дела? Юристы знают
resp.Result.Items[i].JudgeId - системный идентификатор судьи
resp.Result.Items[i].Judge - фамилия И.О. судьи
resp.Result.Items[i].Court - название суда
resp.Result.Items[i].BankruptStage - что-то из юр.терминологии про судопроизводство. Пока попадалось только "Конкурсное производство". Юристы знают.
resp.Result.Items[i].Status - текст про состояние дела?
resp.Result.Items[i].CaseTypeMCode - понятия не имею, что обозначет литера "Б" - код типа дела?
resp.Result.Items[i].CaseCategory - название категории дела, (о банкротстве)
resp.Result.Items[i].CaseType - название типа дела (о несостоятельности ...)
resp.Result.Items[i].ClaimSum - затребованная сумма в рублях?
resp.Result.Items[i].RecoverySum - сумма покрытия?
resp.Result.Items[i].Comment - комментарий? Пока попадался только пустой
resp.Result.Items[i].Instances - список инстанций (судов) по которым дело проходит. Подробности ниже
resp.Result.Items[i].Sides - список участвующих сторон, часто длинный. Подробности ниже
resp.Result.Items[i].LastEvents - список последних событий. Подробности ниже
resp.Result.Items[i].NextEvent - null или обьект - следующее запланированное событие. Подробности ниже

resp.Result.Items[i].Instances - список инстанций (судов) по которым дело проходит:

        "Instances": [
          {
            "Court": "АС города Москвы",
            "Judge": "Мироненко Э. В.",
            "CourtTag": "MSK",
            "InstanceLevel": 1,
            "FinishState": 0,
            "FinishDate": "2013-07-15T00:00:00",
            "IncomingDate": "2013-06-19T00:00:00",
            "JudgeId": "d615e644-c551-4d91-877e-72a455e81c2f"
          },
...
          {
            "Court": "ФАС МО",
            "Judge": "Бусарова Л. В.",
            "CourtTag": "FASMO",
            "InstanceLevel": 3,
            "FinishState": 0,
            "FinishDate": null,
            "IncomingDate": "2014-03-06T00:00:00",
            "JudgeId": "df5a5360-e6f0-452c-b057-65744df02307"
          }
        ]

resp.Result.Items[i].Instances[j].Court - название суда
resp.Result.Items[i].Instances[j].Judge - фамилия И.О. судьи
resp.Result.Items[i].Instances[j].CourtTag - территориальная принадлежность суда, что-то типа метки
resp.Result.Items[i].Instances[j].InstanceLevel - уровень инстанции, число
resp.Result.Items[i].Instances[j].FinishState - пока попадались только нули. Конечная инстанция?
resp.Result.Items[i].Instances[j].FinishDate - null или дата завершения рассмотрения дела в этой инстанции?
resp.Result.Items[i].Instances[j].IncomingDate - дата начала рассмотрения дела?
resp.Result.Items[i].Instances[j].JudgeId - системный идентификатор судьи

resp.Result.Items[i].Sides - список участвующих сторон, часто длинный:

        "Sides": [
          {
            "Type": 0,
            "FakeId": 3587005,
            "TypeName": "Истец",
            "OrganizationId": 0,
            "ShortName": "АНГЛО АЙРИШ БЭНК КОРПОРЭЙШН ЛИМИТЕД",
            "Name": "АНГЛО АЙРИШ БЭНК КОРПОРЭЙШН ЛИМИТЕД",
            "IsBranch": false,
            "IsUnique": false,
            "IsNotPrecise": false,
            "Inn": null,
            "Ogrn": null,
            "Okpo": null,
            "Address": "123317, Россия, Москва, Преснеская наб., д. 10 Башня на набережной, Блок В, эт. 17 ЮФ Меджистерс",
            "Region": null,
            "OrgForm": null,
            "HeadFio": null,
            "StorageId": null,
            "HidePersonalData": 0,
            "IsPhysical": false,
            "IsMonitored": false,
            "InFolders": null
          },
...
          {
            "Type": 1,
            "FakeId": 1878768,
            "TypeName": "Ответчик",
            "OrganizationId": 0,
            "ShortName": "ООО \"Компания \"Финансстройинвестмент\"",
            "Name": "ООО \"Компания \"Финансстройинвестмент\"",
            "IsBranch": false,
            "IsUnique": false,
            "IsNotPrecise": false,
            "Inn": "7717532844",
            "Ogrn": null,
            "Okpo": null,
            "Address": "107113, Россия, Москва, Сокольническая пл., д. 4А",
            "Region": null,
            "OrgForm": null,
            "HeadFio": null,
            "StorageId": null,
            "HidePersonalData": 0,
            "IsPhysical": false,
            "IsMonitored": false,
            "InFolders": null
          }
        ]

resp.Result.Items[i].Sides[j].Type - число, тип стороны (1 - ответчик, 0 - истец, и т.д.). Этот параметр отсутствует в оригинальном описании стороны (привносится из дела)
resp.Result.Items[i].Sides[j].TypeName - название типа стороны (ответчик, истец, и т.д.). Этот параметр отсутствует в оригинальном описании стороны (привносится из дела)
resp.Result.Items[i].Sides[j].FakeId - численный псевдо идентификатор стороны, может упоминаться в resp.Result.FoundSideIdByCaseId. Этот параметр отсутствует в оригинальном описании стороны (привносится из дела)
resp.Result.Items[i].Sides[j].OrganizationId - пока попадались только нули
resp.Result.Items[i].Sides[j].ShortName - краткое название стороны
resp.Result.Items[i].Sides[j].Name - название стороны
resp.Result.Items[i].Sides[j].IsBranch - является ли филиалом?
resp.Result.Items[i].Sides[j].IsUnique - пока попадались только false
resp.Result.Items[i].Sides[j].IsNotPrecise - пока попадались только false
resp.Result.Items[i].Sides[j].Inn - ИНН стороны или пустая строка
resp.Result.Items[i].Sides[j].Ogrn - ОГРН, или null или пустая строка
resp.Result.Items[i].Sides[j].Okpo - ОКПО, или null или пустая строка
resp.Result.Items[i].Sides[j].Address - почтовый адрес стороны
resp.Result.Items[i].Sides[j].Region - название территориального региона
resp.Result.Items[i].Sides[j].OrgForm - название организационной формы? Почти всегда null
resp.Result.Items[i].Sides[j].HeadFio - ФИО начальника, почти всегда null
resp.Result.Items[i].Sides[j].StorageId - пока попадались только null
resp.Result.Items[i].Sides[j].HidePersonalData - флажок сокрытия персональных данных (0, 1, null)
resp.Result.Items[i].Sides[j].IsPhysical - является ли сторона физлицом? (true, false)
resp.Result.Items[i].Sides[j].IsMonitored - пока попадались только false
resp.Result.Items[i].Sides[j].InFolders - пока попадались только null и [] - пустой список

resp.Result.Items[i].LastEvents - список последних событий:

        "LastEvents": [
          {
            "Date": "2014-03-20T00:00:00",
            "Description": null,
            "ContentTypes": [
              "Об ознакомлении с материалами дела (ст. 41 АПК)"
            ],
            "DecisionType": "",
            "DocumentId": "2b23b931-9b0b-4926-8483-240ce0393e00",
            "Court": "9 ААС",
            "Judge": null,
            "JudgeId": "00000000-0000-0000-0000-000000000000",
            "Declarer": "ООО \"Компания \"Финансстройинвестмент\"",
            "DeclarerInfo": null,
            "InstanceNumber": "09АП-7189/2014",
            "NeedJudges": false,
            "TypeName": "Ходатайства",
            "DocumentFileName": null
          }
        ]

resp.Result.Items[i].LastEvents[j].Date - дата события
resp.Result.Items[i].LastEvents[j].Description - описание события
resp.Result.Items[i].LastEvents[j].ContentTypes - список вопросов, повестка заседания?
resp.Result.Items[i].LastEvents[j].DecisionType - пока попадались только пустые
resp.Result.Items[i].LastEvents[j].DocumentId - системный идентификатор документа
resp.Result.Items[i].LastEvents[j].Court - название суда
resp.Result.Items[i].LastEvents[j].Judge - фамилия И.О. судьи
resp.Result.Items[i].LastEvents[j].JudgeId - системный идентификатор судьи
resp.Result.Items[i].LastEvents[j].Declarer - название заявителя
resp.Result.Items[i].LastEvents[j].DeclarerInfo - пока попадались только null
resp.Result.Items[i].LastEvents[j].InstanceNumber - номер инстанции? Больше похоже на номер дела
resp.Result.Items[i].LastEvents[j].NeedJudges - нужен ли судья? (true, false)
resp.Result.Items[i].LastEvents[j].TypeName - название типа события
resp.Result.Items[i].LastEvents[j].DocumentFileName - пока попадались только null

resp.Result.Items[i].NextEvent - null или обьект - следующее запланированное событие:

        "NextEvent": {
          "Date": "2014-03-24T12:00:00",
          "Description": "Судебное заседание\n9 ААС, 10 (кабинет 204)",
          "ContentTypes": null,
          "DecisionType": null,
          "DocumentId": "b22e085c-d093-41e7-9680-1ffe19698967",
          "Court": "9 ААС",
          "Judge": null,
          "JudgeId": "00000000-0000-0000-0000-000000000000",
          "Declarer": null,
          "DeclarerInfo": null,
          "InstanceNumber": "09АП-7189/2014",
          "NeedJudges": false,
          "TypeName": null,
          "DocumentFileName": null
        }

resp.Result.Items[i].NextEvent.Date ... см. описание resp.Result.Items[i].LastEvents[j].Date
остальные поля тоже идентичны resp.Result.Items[i].LastEvents[j].*

################################################################################

Поиск сторон - GET http://casebook.ru/api/Search/Sides?name=%E2%84%96+%D0%9065-27211%2F2011

Запрос передается в виде параметра GET запроса
    name=%E2%84%96+%D0%9065-27211%2F2011
где значение параметра, в данном случае № А65-27211/2011 закодировано urlencode
В случае с ИНН, умная машина составляет запрос иначе (возможно, руководствуясь результатами suggest):
    name=7723830905&inn=7723830905

Ответ приходит как обьест JSON

Забегая вперед, можно отметить, что в браузере показываются следующие параметры участников:
Участник
    resp.Result[i].Name - название стороны
Адрес
    resp.Result[i].Address - почтовый адрес стороны
ИНН
    resp.Result[i].Inn - ИНН стороны или пустая строка

Пример пустого ответа
{
  "Message": null,
  "ServerDate": "2014-03-21T15:30:04.0001429+04:00",
  "Success": true,
  "Timings": [
    "Multistat 00:00:00.0010000"
  ],
  "Result": []
}

В ответе нужно поинтересоваться следующими параметрами:
resp.Success - if false - error, что значит - сбой авторизации, сервера или еще чего. Сообщение о неприятностях надо брать в
resp.Message - если все в порядке, то сообщение пустое. Если сообщение есть, то была ошибка или есть предупреждение
    в любом случае непустого сообщения, данные результата недостоверны.
resp.Timings - может быть null или массив строк, применяется при отладке и содержит значения задержек или сообщения о обломе отдельных агентов.
resp.Result - список с данными ответа, может быть пустой. Детально см.ниже.

Пример не пустого Result
  "Result": [
    {
      "OrganizationId": 0,
      "ShortName": "ООО \"Глобинторг\"",
      "Name": "Общество с ограниченной ответственностью \"Глобинторг\"",
      "IsBranch": false,
      "IsUnique": false,
      "IsNotPrecise": false,
      "Inn": "7723830905",
      "Ogrn": "1127746178867",
      "Okpo": "9136445",
      "Address": "109263, г Москва, ул Чистова, д 12 А",
      "Region": "Москва и Московская область",
      "OrgForm": "Общества с ограниченной ответственностью",
      "HeadFio": "Сафонтьевская Наталья Анатольевна",
      "StorageId": null,
      "HidePersonalData": null,
      "IsPhysical": false,
      "IsMonitored": false,
      "InFolders": []
    }
  ]

resp.Result[i].OrganizationId - пока попадались только нули
resp.Result[i].ShortName - краткое название стороны
resp.Result[i].Name - название стороны
resp.Result[i].IsBranch - является ли филиалом?
resp.Result[i].IsUnique - пока попадались только false
resp.Result[i].IsNotPrecise - пока попадались только false
resp.Result[i].Inn - ИНН стороны или пустая строка
resp.Result[i].Ogrn - ОГРН, или null или пустая строка
resp.Result[i].Okpo - ОКПО, или null или пустая строка
resp.Result[i].Address - почтовый адрес стороны
resp.Result[i].Region - название территориального региона
resp.Result[i].OrgForm - название организационной формы? Почти всегда null
resp.Result[i].HeadFio - ФИО начальника, почти всегда null
resp.Result[i].StorageId - пока попадались только null
resp.Result[i].HidePersonalData - флажок сокрытия персональных данных (0, 1, null)
resp.Result[i].IsPhysical - является ли сторона физлицом? (true, false)
resp.Result[i].IsMonitored - пока попадались только false
resp.Result[i].InFolders - пока попадались только null и [] - пустой список

Следует отметить, что при поиске дел, в ответе на запрос, к каждому найденному делу придается список сторон.
Суть в том, что в каждой найденной по делу стороне есть доп.атрибуты, которых нет в "просто" стороне:
    resp.Result.Items[i].Sides[j].Type - число, тип стороны (1 - ответчик, 0 - истец, и т.д.). Этот параметр отсутствует в оригинальном описании стороны (привносится из дела)
    resp.Result.Items[i].Sides[j].TypeName - название типа стороны (ответчик, истец, и т.д.). Этот параметр отсутствует в оригинальном описании стороны (привносится из дела)
    resp.Result.Items[i].Sides[j].FakeId - численный псевдо идентификатор стороны, может упоминаться в resp.Result.FoundSideIdByCaseId. Этот параметр отсутствует в оригинальном описании стороны (привносится из дела)

################################################################################

Примеры поисковых запросов

Поиск по делам

{{{
№ А40-51217/2011
    запрос/ответ (3) в файле
        data/query.case01.json
    Отображается в браузере как:
        data/casebook.case01.result01.png

№ А65-27211/2011
    запрос/ответ (3, cases - Warnings - datasource timeout) в файле
        data/query.case02.json
    Отображается в браузере как:
        data/casebook.case02.result01.png

№ А40-27010/2012
    запрос/ответ (2) в файле
        data/query.case03.json
    Отображается в браузере как:
        data/casebook.case03.result01.png
}}}


Поиск по юридическим лицам (компаниям)

{{{
ОАО «ЛУКОЙЛ-Коми» (ИНН 1106014140 )
    запрос/ответ (3, cases - Warnings) в файле
        data/query.company01.json
    Отображается в браузере как:
        data/casebook.company01.result01.png

компания «Демесне Инвестментс Лимитед»
    запрос/ответ (3, cases - Warnings) в файле
        data/query.company02.json
    Отображается в браузере как:
        data/casebook.company02.result01.png

ОАО «Глобинторг» (ИНН 7723830905)
    это очень интересный вариант - поиск по делам ничего не находит, но находит поиск по сторонам (sides) если указать
    ИНН http://casebook.ru/api/Search/Sides?name=7723830905&inn=7723830905
    запрос/ответ (3) в файле
        data/query.company03.json
    Отображается в браузере как:
        data/casebook.company03.result01.png
}}}


Поиск по физическим лицам

{{{
Волков Валерий Юрьевич
    запрос/ответ (3, cases - Warnings) в файле
        data/query.person01.json
    Отображается в браузере как:
        data/casebook.person01.result01.png

Габдрахимов Александр Мухаматшевич - нет такого
Габдрахимов Александр Мухаметшевич
    с добавкой suggest, откуда видно, что запрашивать можно дела, стороны, судей, суды
    запрос/ответ (3) в файле
        data/query.person02.json
    Отображается в браузере как:
        data/casebook.person02.result01.png

Шейдорова Александра Витальевна
    запрос/ответ (3) в файле
        data/query.person03.json
    Отображается в браузере как:
        data/casebook.person03.result01.png
}}}

################################################################################

Возможно получение таких сообщений, данных либо нет вообще, либо данные не все

HTTP/1.0 200 OK
Cache-Control: no-cache
Pragma: no-cache
Content-Length: 547
Content-Type: application/json; charset=utf-8
Expires: -1
Server: Microsoft-IIS/7.5
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
X-Powered-By: ARR/2.5
X-Powered-By: ASP.NET
Date: Thu, 20 Mar 2014 16:50:59 GMT
X-Cache: MISS from gate.algis.com
X-Cache-Lookup: MISS from gate.algis.com:3128
Via: 1.1 gate.algis.com:3128 (squid/2.7.STABLE9)
Connection: keep-alive
Proxy-Connection: keep-alive

{
  "Message": "Результаты собраны не из всех источников. Повторите запрос позже для уточнения",
  "ServerDate": "2014-03-20T20:50:59.0003827+04:00",
  "Result": {
    "MaxSum": -1.0,
    "FoundSideIdByCaseId": {},
    "Page": 1,
    "PageSize": 30,
    "TotalCount": 0,
    "PagesCount": 0,
    "Items": []
  },
  "Success": true,
  "Timings": [
    "GetCasesIdsFormSpx 00:00:03.0700000",
    "Warnings:index ix_sides: agent cg-sps11:3327: query timed out"
  ]
}

################################################################################

Вопрос: что делать с этими запросами и результатами запросов

Допустим так:
на вход читателя поступает список строк - что интересует пользователей.
Пример:

    № А40-51217/2011
    № А65-27211/2011
    № А40-27010/2012
    ОАО «ЛУКОЙЛ-Коми» (ИНН 1106014140 )
    компания «Демесне Инвестментс Лимитед»
    ОАО «Глобинторг» (ИНН 7723830905)
    Волков Валерий Юрьевич
    Габдрахимов Александр Мухаметшевич
    Шейдорова Александра Витальевна

Пусть это будет файл
    data/input.lst

Далее, читатель по каждой строке из этого файла выполняет два запроса:
    POST http://casebook.ru/api/Search/Cases
    GET http://casebook.ru/api/Search/Sides
с передачей данной строки в соответствующих параметрах.

Результат каждого запроса сохраняется в файл по шаблону:
    data/query.{hash}.(cases|sides).json

где {hash} это дайджест поисковой строки.
Дополнительно, информация о запросе/ответе сохраняется в индексный файл:
    index.json

Формат записи приблизительно такой:
{
  "queries": {
    "Волков Валерий Юрьевич": {
      "casesCount": 3,
      "casesRespError": "",
      "casesRespFile": "/home/valik/data/projects/casebook.ripper/data/query.58f3e84d771a278f68a5fba36213cc752f0d4bef.cases.json",
      "casesRespWarning": "",
      "qryString": "Волков Валерий Юрьевич",
      "sidesCount": 0,
      "sidesRespError": "",
      "sidesRespFile": "/home/valik/data/projects/casebook.ripper/data/query.58f3e84d771a278f68a5fba36213cc752f0d4bef.sides.json",
      "sidesRespWarning": ""
    },
    ...
  }
}


################################################################################

Разбор трафика браузера при собирании информации по делам и участникам

После первичного поиска мы имеем список cases (дела) и список sides (участники).
Используя информацию из этих списков надо забрать следующую информацию.

Для каждого дела:
    карточка дела GET http://casebook.ru/api/Card/Case?id=78d283d0-010e-4c50-b1d1-cf2395c00bf9
        GET http://casebook.ru/api/Card/InstanceDocuments?id=9c80dae7-7cc3-4724-80e5-84d6fa6361e3
        POST http://casebook.ru/api/Card/PdfDocumentArchiveInstanceCount/9c80dae7-7cc3-4724-80e5-84d6fa6361e3
    Скачать документы
        GET http://casebook.ru/File/PdfDocumentArchiveCase/fbafd1b2-e22d-496c-a6f9-6a94b2d1effc/%D0%9058-734-2014.zip
    Участники дела
        Истцы (side/info)
        Ответчики (side/info)
        Третьи лица
        Иные лица
        документы
            GET http://casebook.ru/api/Card/CaseDocuments?id=fbafd1b2-e22d-496c-a6f9-6a94b2d1effc
    Суды и судьи
        Судья (judge/ifo)
            Информация
                GET http://casebook.ru/api/Card/Judge/d3672703-af3a-4500-bacb-ffded24067f1

Для каждого участника:
    (side/info) подробная информация
        POST http://casebook.ru/api/Card/BusinessCard
        POST http://casebook.ru/api/Card/BankruptCard
        GET http://casebook.ru/api/Search/SidesDetailsEx
        GET http://casebook.ru/api/Card/Excerpt?Address=...
        история изменений руководителя
            POST http://casebook.ru/api/Card/RequestPersonInfo/750349
            GET http://casebook.ru/api/Card/CheckRequestStates/677732
            GET http://casebook.ru/api/Notification/GetLastNormalize/677732
        (side/head) сведения о руководителе GET http://casebook.ru/api/Card/Person/750349
        (side/info) учредители
        (side/info) учрежденные
        Отчетность (POST http://casebook.ru/api/Card/AccountingStat)
        Арбитражные дела (POST http://casebook.ru/api/Search/Cases)
            (POST http://casebook.ru/api/Card/OrgStatShort)
            расписание на месяц (POST http://casebook.ru/api/Calendar/Period)
                документы (GET http://casebook.ru/File/PdfDocument/18f5a877-751c-426a-a0b9-ef49c0b8dd16/A33-5491-2013_20131024_Reshenie.pdf)
                    GET http://casebook.ru/File/PdfDocument/af6407d6-47dd-428f-9f2b-184af0b3e6da/A58-1045-2014_20140311_Opredelenie.pdf
        Дела СОЮ (POST http://casebook.ru/api/Search/CasesGj)

################################################################################

Пример. Дело № А40-27010/2012
Поиск находит одно дело, показывает список http://casebook.ru/#selection/cases
участников не показывает, СОЮ не показывает.
Для каждого дела:
    получить подробную информацию, используя resp.Result.Items[i].CaseId (78d283d0-010e-4c50-b1d1-cf2395c00bf9)
    карточка дела GET http://casebook.ru/api/Card/Case?id=78d283d0-010e-4c50-b1d1-cf2395c00bf9
    сколько документов POST http://casebook.ru/api/Card/PdfDocumentArchiveCaseCount/78d283d0-010e-4c50-b1d1-cf2395c00bf9
    инфо по документам GET http://casebook.ru/api/Card/CaseDocuments?id=78d283d0-010e-4c50-b1d1-cf2395c00bf9
    архив документов http://casebook.ru/File/PdfDocumentArchiveCase/78d283d0-010e-4c50-b1d1-cf2395c00bf9/%D0%9040-27010-2012.zip
        где %D0%9040-27010-2012.zip - желаемое имя файла
    документы по инстанциям (номер брать из Card/Case resp.Result.Case.Instances[i].Id)
        GET http://casebook.ru/api/Card/InstanceDocuments?id=b55f3d6b-10f3-42c4-a28b-48528f11dc15
        POST http://casebook.ru/api/Card/PdfDocumentArchiveInstanceCount/b55f3d6b-10f3-42c4-a28b-48528f11dc15
            без payload
    для всех (side/info) для участников - истцы, ответчики, третьи лица, иные (параметры запроса берутся из инфы по делу)
        POST http://casebook.ru/api/Card/BusinessCard
            пример payload запроса {"Address":"Данные скрыты","Inn":"","Name":"Гурняк Я. Ф.","Ogrn":"","Okpo":"","IsNotPrecise":true,"OrganizationId":""}
        POST http://casebook.ru/api/Card/BankruptCard
            payload такой же

Если кратко, порядок запросов такой:
search.cases
for each case from search
    card.case
    Card.PdfDocumentArchiveCaseCount - just num of docs - skip it
    card.casedocuments
    File.PdfDocumentArchiveCase
    for each side
        card.bankruptcard
        card.businesscard
    for each judge
        Card.Judge

################################################################################

Поиск участников

Если кратко, порядок запросов такой:
search.sides ОАО «ЛУКОЙЛ-Коми» (ИНН 1106014140 )
for each side
    card.accountingstat.saz
    card.excerpt.saz
    search.sidesdetailsex.saz
    search.cases.saz    search.cases2.saz (for each side mentioned)
    search.casesgj.saz
    calendar.period.saz
    card.bankruptcard.saz
        case info for each case mentioned
    card.businesscard.saz
        Founders - side info for each side mentioned
        for each founder (side)
            search cases

    test and tune for other side cards

################################################################################

Этап сбора информации через Fiddler. Что доступно из браузера

Участники (#selection/sides)
    показывает список типа Название, Адрес, ИНН
    можно пойти по ссылке типа (side/info)
    можно открыть карточку inplace
        GET http://casebook.ru/api/Search/SidesDetailsEx?index=7&inn=4345338310&okpo=10921600
        POST http://casebook.ru/api/Search/Cases
        показывает список дел (дело, участники, инстанции, события)
            можно открыть карточку дела в новом окне http://casebook.ru/#case/1e56dba1-8f0d-4756-9f39-29d30bd449dd
                GET http://casebook.ru/api/Card/Case?id=1e56dba1-8f0d-4756-9f39-29d30bd449dd
        можно перейти по ссылке (открыть карточку) типа (side/info)

Арбитражные дела (#selection/cases)
    показывает список дел (дело, участники, инстанции, события)
    можно открыть карточку inplace
    ссылки на дела типа (http://casebook.ru/#case/fbafd1b2-e22d-496c-a6f9-6a94b2d1effc)
        страница аналогично Выбрал дело/Открыть карточку
    ссылки на судью типа (http://casebook.ru/#judge/info/d3672703-af3a-4500-bacb-ffded24067f1)

    выбрал дело "Number": "А54-1530/2014"
    открыл карточку inplace
    получил запросы
        GET http://casebook.ru/api/Card/Case?id=114e4866-fd5a-4330-a146-53f33083374b
        POST http://casebook.ru/api/Card/PdfDocumentArchiveCaseCount/114e4866-fd5a-4330-a146-53f33083374b
        GET http://casebook.ru/api/Card/CaseDocuments?id=114e4866-fd5a-4330-a146-53f33083374b
    В интерфейсе есть:
        Открыть карточку
            GET http://casebook.ru/api/Card/InstanceDocuments?id=9c80dae7-7cc3-4724-80e5-84d6fa6361e3
            POST http://casebook.ru/api/Card/PdfDocumentArchiveInstanceCount/9c80dae7-7cc3-4724-80e5-84d6fa6361e3
        Скачать документы (GET http://casebook.ru/File/PdfDocumentArchiveCase/fbafd1b2-e22d-496c-a6f9-6a94b2d1effc/%D0%9058-734-2014.zip)
        Истцы (side/info)
        Ответчики (side/info)
        Третьи лица
        Иные лица
        Судья (judge/ifo)
{{{
Выбрал дело/Открыть карточку в новом окне (Case?id=fbafd1b2-e22d-496c-a6f9-6a94b2d1effc)
получил запросы (некоторые повторяются)
    GET http://casebook.ru/api/Card/InstanceDocuments?id=9c80dae7-7cc3-4724-80e5-84d6fa6361e3
    POST http://casebook.ru/api/Card/PdfDocumentArchiveInstanceCount/9c80dae7-7cc3-4724-80e5-84d6fa6361e3
В интерфейсе есть:
    Скачать карточку (POST http://casebook.ru/File/Pdf)
    Скачать документы (GET http://casebook.ru/File/PdfDocumentArchiveCase/fbafd1b2-e22d-496c-a6f9-6a94b2d1effc/%D0%9058-734-2014.zip)
    Участники дела
        Истцы (side/info) (POST http://casebook.ru/api/Card/BusinessCard)
            POST http://casebook.ru/api/Card/BankruptCard
        Ответчики (side/info) (см.Истцы)
        Третьи лица
        Иные лица
        документы (GET http://casebook.ru/api/Card/CaseDocuments?id=fbafd1b2-e22d-496c-a6f9-6a94b2d1effc)
    Суды и судьи
        Судья (judge/ifo)
            Информация (GET http://casebook.ru/api/Card/Judge/d3672703-af3a-4500-bacb-ffded24067f1)
            Дела (POST http://casebook.ru/api/Search/Cases)
    Судебные акты (GET http://casebook.ru/api/Card/CaseDocuments?id=fbafd1b2-e22d-496c-a6f9-6a94b2d1effc)

Выбрал дело/Открыть карточку/Участники дела - Истцы (конкр.истец)
    POST http://casebook.ru/api/Card/BusinessCard
    POST http://casebook.ru/api/Card/BankruptCard
в интефейсе есть:
    Выписка из ЕГРЮЛ (GET http://casebook.ru/api/Card/Excerpt?Address=...)
    Об участнике
        история изменений руководителя (POST http://casebook.ru/api/Card/RequestPersonInfo/750349)
            GET http://casebook.ru/api/Card/CheckRequestStates/677732
            GET http://casebook.ru/api/Notification/GetLastNormalize/677732
            (side/head) GET http://casebook.ru/api/Card/Person/750349
        учредители (side/info)
        учрежденные (side/info)
    Отчетность (POST http://casebook.ru/api/Card/AccountingStat)
    Арбитражные дела (POST http://casebook.ru/api/Search/Cases)
        (POST http://casebook.ru/api/Card/OrgStatShort)
        Экспорт (POST http://casebook.ru/File/ExportSearchCsv/)
            CSV
        расписание на месяц (POST http://casebook.ru/api/Calendar/Period)
            документы (GET http://casebook.ru/File/PdfDocument/18f5a877-751c-426a-a0b9-ef49c0b8dd16/A33-5491-2013_20131024_Reshenie.pdf)
                GET http://casebook.ru/File/PdfDocument/af6407d6-47dd-428f-9f2b-184af0b3e6da/A58-1045-2014_20140311_Opredelenie.pdf
    Дела СОЮ (POST http://casebook.ru/api/Search/CasesGj)
        Экспорт CSV (POST http://casebook.ru/File/ExportGjSearchCsv/)
}}}

Дела СОЮ (http://casebook.ru/#selection/general)
    POST http://casebook.ru/api/Search/CasesGj
    показывает список дел (дело, участники, инстанции, судья, события)
    можно открыть карточку дела в новом окне (#general/8c47f6fb-e1fe-4768-b3db-268caef3f6ea)
        GET http://casebook.ru/api/Card/GjCase?id=76e00283-876e-4354-a4fa-f5c562710e05
        показывает участников дела (side/info)
    можно развернуть карточку inplace
        показывает участников дела (side/info)

################################################################################

Теперь следующий шаг: пользуясь результатами поисковых запросов вытягивать "всю" информацию с сайта.
Понадобится день-два (реально 7).

Потом надо решать, что делать с полученными данными.
Вариант 1: делать по быстрому веб-сервис на Монге.
Вариант 2: делать по долгому хранение в БД SQL.
Вариант 3: делать прокси к кейсбуку.

Сервис на Монге можно сделать дней за 20 - без поиска, простая выдача перечней дел, сторон и проч.
Без навороченной структуры, самый минимум.
Примитивно, зато работает. Потом можно постепенно расширять и дополнять,
прикручивать поиск, выдачу XML, экспорт в XLS и проч.

Хранение в SQL потребует больше времени, раза в полтора, может два, ибо много аналитической работы.
Выделить сущности и связи, нормализовать, нарисовать схему, создать БД, написать бизнес логику вставки/удалений/обновлений данных,
написать парсеры, загрузчики.
Короче, SQL предьявляет строгие требования к качеству данных. Монга - нет.
И после всего этого будет БД, но не будет интерфейса для пользователя. Его еще надо будет делать как-то.

################################################################################

2014-06-02 Поговорили и выяснили

Целей у проекта две:

    1. Обеспечить доступ к информации Кейсбука для нескольких пользователей (до 50, к примеру) используя одну учетку на Кейсбуке.
        Доступ означает - искать и просматривать информацию онлайн; подписываться на события/изменения в делах/участниках дел.
    2. Обеспечить руководству компании мониторинг деятельности пользователей.
        Смысл мониторинга - знать кто, когда, каким делом/участником занят.

Первая цель достигается решением задачи построения "прокси", цитирую из отчета:
Собственно, зачем нужно перекладывать данные из casebook.ru в свою БД?
Можно сделать веб-сервис класса прокси (proxy), который будет принимать запросы пользователей и перенаправлять их на
casebook.ru, транслируя ответы обратно.
Подробнее об этом было написано в отчете.

Вторая цель (мониторинг) может быть достигнута в отрыве от первой, что возможно если вторая цель приоритетнее, важнее.
Для этого надо решить следующие задачи.

Изготовление интерфейса пользователя, через который он вносит заявку на отслеживание дела/участника.
Например, это может быть форма с таким набором полей:

    * email по которому отправлять уведомления.
    * Номер отслеживаемого дела или атрибуты участника (название, ИНН, адрес, ОГРН, ОКПО).
    * периодичность проверки данных на наличие новостей.

Изготовление интерфейса пользователя, через который он контролирует свои заявки - исправляет, удаляет.
Обычно это делается как список или таблица имеющихся заявок с переходом на форму редактирования/удаления элемента.

Создание БД учета заявок.
Данные по заявкам надо где-то хранить. Это удобнее делать в SQL базе данных, особенно с учетом того,
что информация из этой БД позволяет формировать требуемые отчеты для руководства - желаемый мониторинг.

Создание механизма обработки заявок.
Обработка подразумевает обеспечение обновления данных.
Каждая заявка, помимо того, что может быть активна/закрыта, содержит что-то вроде расписания для проверки -
нет ли новостей. Нужен механизм, который по расписанию для каждой заявки запускает процедуру поиска новостей/сбора данных.
Короче, что-то вроде процедуры в БД, запускаемой раз в час, к примеру. Эта процедура обходит все активные заявки
и по каждой собирает сведения из Кейсбука согласно заявленной периодичности.

Создание робота забирающего информацию из Кейсбука согласно заявки.
Механизм обработки заявок не сам лезет в Кейсбук. Он запускает робота-читателя, передавая ему параметры заявки.
Читатель забирает из Кейсбука требуемые сведения и записывает их в БД в виде, пригодном для дальнейшей обработки.

Создание БД хранения данных, собранных по заявкам.
Данные взятые из Кейсбука надо где-то хранить. Удобнее это делать в БД типа MongoDB.
Очевидно, чтобы иметь возможность определять наличие новостей, хранить надо минимум две версии данных.
Удобно сохранять ровно тот минимум данных, который позволяет определить наличие изменений, все остальное
можно получить по ссылке на определенную страницу Кейсбука (или страницу прокси).
Отдельно следует учесть информацию по делам, выраженную в виде календарных событий.
Эти сведения необходимо сохранять в SQL БД для последующего отражения в отчетности.

Создание робота обработки данных, выявляющего события/изменения в делах/участниках.
Робот-читатель не занимается обработкой данных, это поручается отдельному механизму, роботу-отличатору.
Этот робот запускается по сигналу готовности данных (окончено скачивание) или по расписанию.
Для каждой активной заявки он берет две версии данных, сравнивает их и определяет наличие изменений.
Каждое изменение оформляется как некое событие и сохраняется в БД.
Возможно, несколько изменений по одной заявке надо расценивать как одно событие, чтобы не плодить лишних уведомлений.

Создание БД учета событий/изменений.
Факт наличия изменений в данных, собираемых по заявке, наравне с версиями данных, надо где-то хранить.
Удобно это делать в SQL БД, хотя я уверен в этом не на 100%.
Пусть это будет БД "событий" или "новостей", где каждое событие отражает заявку, к которой относится,
время обнаружения события, содержимое изменений - что было и что стало.

Создание механизма обработки событий/изменений.
Последний шаг в цепочке отработки заявок. Некая процедура по расписанию проверяет наличие
свежих событий/новостей и выполняет работу по рассылке уведомлений и/или отчетов заинтересованным лицам.

Теперь, после решения предыдущих задач, можно достичь цели - мониторинг деятельности пользователей.
Для этого достаточно придумать (и реализовать) формы отчетов, изготавливаемых из имеющихся данных:
пользователи, дела на которые подписаны пользователи, участники на которых подписаны пользователи,
календарные события по делам.

################################################################################

Приложение

Вырезки из информации получаемой из Кейсбука о делах/участниках, для занесения в базу данных.
В БД должно храниться минимум две версии таких вырезок - предыдущая и текущая.
Эти данные забираются из casebook.ru при нажатии на условную кнопку "отслеживать изменения" aka "подписка",
в дальнейшем происходит периодическая проверка - не было ли изменений в этих данных.
Если изменения обнаружены, подписчику высылается уведомление.

Здесь мои предположения и соображения. У адвокатов/пользователей могут быть другие соображения на эту тему.
Полные примерные выборки данных см.в файле data.samples.zip

Участники (side)

Calendar/Period
Сведения по событиям за запрошенный период (предполагаю, что запрашивать надо период = месяц с текущей даты)

Представляет собой список событий (длина списка заранее неизвестна).
Предполагаю, что это список слушаний (рассмотрений дел), в которых участвует заявленная сторона.
Каждый элемент списка выглядит примерно так (лишнее удалено):

{
  "HearingDate": "2014-05-29T11:10:00",
  "HearingPlace": "115",
  "CaseNumber": "А56-7785/2010",
  "JudgeName": "Фуркало О. В.",
  "CourtName": "АС города Санкт-Петербурга и Ленинградской обл.",
  "BankruptStage": "Конкурсное производство",
  "LastEvent": {},
  "BaseEvent": {},
  "Sides": [],
}

Три последних элемента - сложные объекты:
    "Sides": [],
представляет собой список участников дела (длина заранее неизвестна).
    "LastEvent": {},
    "BaseEvent": {},
представляют собой объекты одинаковой структуры с информацией о рассмотрении в суде?
Предполагаю, что все три элемента могут быть не важны для наших целей.

Примерный вид этих элементов:

"LastEvent": {
или
"BaseEvent": {
    "Date": "2014-04-24T00:00:00",
    "Description": "",
    "ContentTypes": [ // список
      "Определение об отложении судебного разбирательства"
    ],
    "DecisionType": "",
    "Court": "АС города Санкт-Петербурга и Ленинградской обл.",
    "Judge": "Фуркало О. В.",
    "InstanceNumber": "А56-7785/2010",
    "NeedJudges": true,
    "TypeName": "Информация о принятом судебном акте",
  }

"Sides": [ // список заранее неизвестной длины, тут показаны три первых элемента списка
    {
      "TypeName": "Кредитор",
      "ShortName": "Фатеева Н. П.",
      "Name": "Фатеева Н. П.",
      "Inn": null,
      "Ogrn": null,
      "Okpo": null,
      "Address": "город Ижевск",
      "IsPhysical": true,
    },
    {
      "TypeName": "Истец",
      "ShortName": ".ОАО \"Севкабель\"",
      "Name": ".ОАО \"Севкабель\"",
      "Inn": null,
      "Ogrn": null,
      "Okpo": null,
      "Address": "199106, Россия, Санкт-Петербург, Кожевенная линия, д. 40",
      "IsPhysical": false,
    },
    {
      "TypeName": "Ответчик",
      "ShortName": "ЗАО АКБ ТрансКапиталбанк",
      "Name": "ЗАО АКБ ТрансКапиталбанк",
      "Inn": null,
      "Ogrn": null,
      "Okpo": null,
      "Address": "191119, Россия, Санкт-Петербург, ул. Звенигородская, д.22",
      "IsPhysical": false,
    }
  ],

Card/BankruptCard
Сведения о делах (слушаниях?) по банкротству заявленной стороны.
Объект содержит внутри список дел (слушаний) по банкротству.
Предполагаю, что эти сведения могут быть не важны для наших целей.

Пример:

{
    "CaseNumber": "А40-153223/2012",
    "Date": "2012-11-22T00:00:00",
    "RegistryCloseDate": null,
    "State": "Заявление не принято, возвращено или оставлено без рассмотрения",
    "Cases": [ // список, в данном примере из одного элемента
      {
        "Number": "А40-153223/2012",
        "Date": "2013-02-01T00:00:00",
        "StartDate": "2012-11-22T00:00:00",
        "RegistryCloseDate": null,
        "State": "Заявление не принято, возвращено или оставлено без рассмотрения",
      }
    ]
}

Card/BusinessCard
Подробная информация о заявленном участнике (side).
Предполагаю, что здесь может быть интересна только общая информация, что тут мониторить на изменения?
Вероятно, достаточно складывать в БД только набор:
    "Okpo": "29034830",
    "Ogrn": "1027700431296",
    "Inn": "7710401987",
    "Name": "Закрытое акционерное общество коммерческий банк \"Ситибанк\"",
    "Address": "125047, г Москва, ул Гашека, д 8-10, корпус 1",
используя которые можно всегда открыть страницу Кейсбука (или прокси) с детальной информацией.

Пример:

{
    "Fax": "643-14-01",
    "Email": "",
    "Capital": "1000000000",
    "LastUpdate": "2013-10-11T04:06:06",
    "Okpo": "29034830",
    "Ogrn": "1027700431296",
    "Inn": "7710401987",
    "Name": "Закрытое акционерное общество коммерческий банк \"Ситибанк\"",
    "ShortName": "ЗАО КБ \"Ситибанк\"",
    "Address": "125047, г Москва, ул Гашека, д 8-10, корпус 1",
    "Phone": "495-643-14-25",
    "Chief": {
      "Date": "2013-10-11T04:06:06",
      "Name": "Турек Зденек",
      "Post": "Президент",
    },
    "Status": {
      "Date": "2003-03-17T00:00:00",
      "Value": {
        "Name": "действующее",
        "ShortName": "активное"
      }
    },
    "AffiliatedOrganizations": [ // список произвольной длины
      {
        "Sum": "1688368.00",
        "Percent": "7.94",
        "Capital": "21264081.37",
        "Okpo": "44434",
        "Ogrn": "1027700035769",
        "Inn": "7708004767",
        "Name": "Открытое акционерное общество \"Нефтяная компания \"ЛУКОЙЛ\"",
        "ShortName": "ОАО \"Нефтяная компания \"ЛУКОЙЛ\"",
        "Address": "101000, г Москва, бульв Сретенский, д 11",
      },
    ]
}

Обратите внимание, что внутри содержатся сложные объекты
    "Chief": {
    "Status": {
    "AffiliatedOrganizations": [ // список произвольной длины

Search/Cases
Результаты поиска дел с участием заявленной стороны.
Дела (cases) и информация по слушаниям (инстанциям?).
Предполагаю, что вся эта информация должна быть в календаре (см.выше), поэтому,
вероятно, можно ее в БД не фиксировать. Или наоборот, календарь не сохранять а сохранять результаты
такого поиска, для последующего сравнения и мониторинга.

Пример:

{
    "TotalCount": 30,
    "Page": 1,
    "PageSize": 30,
    "PagesCount": 1,
    "Items": [ // список произвольной длины
      {
        "CaseNumber": "А40-150564/2013",
        "StartDate": "2013-10-23T00:00:00",
        "Judge": "Еремина И. И.",
        "Court": "АС города Москвы",
        "BankruptStage": "",
        "Status": "Рассматривается в апелляционной и первой инстанциях",
        "CaseType": "экономические споры по гражданским правоотношениям",
        "ClaimSum": 0.0,
        "RecoverySum": null,
        "Instances": [ // список произвольной длины
          {
            "Court": "9 ААС",
            "Judge": "Левченко Н. И.",
            "FinishState": 0,
            "FinishDate": null,
            "IncomingDate": "2014-05-20T00:00:00",
          }
        ],
        "Sides": [ // список произвольной длины
          {
            "TypeName": "Истец",
            "ShortName": "ЗАО \"Титан\"",
            "Name": "ЗАО \"Титан\"",
            "Inn": "7733745173",
            "Ogrn": null,
            "Okpo": null,
            "Address": "141006, Россия, Москва, Олимпийский проспект, д.38",
            "IsPhysical": false,
          },
        ],
        "LastEvents": [ // список произвольной длины
          {
            "Date": "2014-05-27T00:00:00",
            "Description": null,
            "ContentTypes": [
              "Принять к производству апелляционную жалобу. Назначить дело к судебному разбирательству (ст. 261 АПК)"
            ],
            "DecisionType": "",
            "Court": "9 ААС",
            "Judge": "Левченко Н. И.",
            "Declarer": "",
            "InstanceNumber": "09АП-20976/2014",
            "NeedJudges": true,
            "TypeName": "Определение",
          },
        ],
        "NextEvent": {
          "Date": "2014-07-09T14:45:00",
          "Description": "Судебное заседание\n9 ААС, 8 (кабинет  202)",
          "ContentTypes": null,
          "DecisionType": null,
          "Court": "9 ААС",
          "Judge": null,
          "Declarer": null,
          "InstanceNumber": "09АП-20976/2014",
          "NeedJudges": false,
          "TypeName": null,
        },
      },
    ],
}

Search/CasesGj
Аналогично Search/Cases
только для судов общей юрисдикции.

Пример:

{
    "Page": 1,
    "PageSize": 30,
    "PagesCount": 5,
    "TotalCount": 125,
    "Items": [ // список произвольной длины
      {
        "CaseNumber": "М-973/2014",
        "StartDate": "2014-02-20T00:00:00",
        "Judge": "Кожевникова Н.В.",
        "Court": "Мытищинский городской суд (Московская область)",
        "BankruptStage": null,
        "Status": "Рассмотрение дела завершено",
        "IsGJ": true,
        "IsSimpleJustice": false,
        "Sides": [ // список произвольной длины
          {
            "TypeName": "ИСТЕЦ",
            "ShortName": "Воронин Ю.В.",
            "Name": "Воронин Ю.В.",
            "Inn": null,
            "Ogrn": null,
            "Okpo": null,
            "Address": "Информация не заполнена",
            "IsPhysical": true,
          },
        ],
        "LastEvents": [ // список произвольной длины
          {
            "Date": "2014-02-20T13:43:00",
            "Description": null,
            "ContentTypes": [
              "Передача материалов судье"
            ],
            "DecisionType": "",
            "Court": "Мытищинский городской суд (Московская область)",
            "Judge": "Кожевникова Н.В.",
            "Declarer": "",
            "InstanceNumber": "М-973/2014",
            "NeedJudges": true,
            "TypeName": "Передача материалов судье",
          },
        ],
        "NextEvent": null,
      },
    ],
}

Дела (case)

Card/Case
Подробная информация по интересующему делу.
Очень много всего, тут только юрист может разобраться, что надо учитывать/мониторить, что не надо.

Пример:

{
    "InstanceUpdates": {},
    "CreditorsInfo": null,
    "SideExclusions": null,
    "ResponsibleUser": null,
    "Case": {
      "Number": "А40-27010/2012",
      "ClaimSum": 0.0,
      "RecoverySum": 0.0,
      "CaseType": "экономические споры по гражданским правоотношениям",
      "CourtName": "АС города Москвы",
      "RegistrationDate": "2012-02-09T00:00:00",
      "RegistryCloseDate": null,
      "BankruptStage": "",
      "CaseStage": "Подана кассационная жалоба",
      "IsSimpleJustice": false,
      "Instances": [ // список произвольной длины
        {
          "InstanceValidNumber": "Ф05-2949/2014",
          "InstanceOriginalNumber": "Ф05-2949/14",
          "CourtName": "ФАС МО",
          "CourtTag": "FASMO",
          "StartDate": "2014-03-12T00:00:00",
          "NextSessionDate": null,
          "NextSessionPlace": null,
          "SuspendUntil": null,
          "FinalDocument": {
            "Type": "Решения и постановления",
            "FinishInstance": 1,
            "ContentTypes": [
              "Постановление (определение) суда кассационной инстанции"
            ],
            "PublishDate": null,
            "DisplayDate": "01.04.2014",
            "AppealDate": "2014-07-02T00:00:00",
            "ActualDate": "2014-04-01T00:00:00",
            "DecisionType": "Оставить определение без изменения, кассационную жалобу без удовлетворения",
            "ClaimSum": 0.0,
            "IsStart": false,
            "IsAct": true,
            "Judges": [],
            "Declarers": [],
            "HearingDate": null,
            "HearingPlace": null,
            "AppealState": null,
            "AppealDescription": "",
            "Addressee": null,
            "IsDeleted": false,
            "DelDate": null,
          },
          "StartDocInfo": {
            "DocType": "Кассационная жалоба",
            "ApeealedType": "Определение о возвращении апелляционной жалобы",
            "Declarers": [ // список произвольной длины
              {
                "Organization": "Гурняк Я. Ф.",
                "Address": "814000, Львовская обл г. Самбор ул. Грабовского д. 15",
                "Inn": "",
                "Ogrn": "",
                "Type": 0
              }
            ]
          },
        },
      ],
      "Judges": [ // список произвольной длины
        {
          "Name": "АС города Москвы",
          "Judges": [
            {
              "Name": "Лисицын К. В."
            }
          ]
        },
      ],
      "Sides": {
        "Plaintiffs": [ // список произвольной длины
          {
            "Type": "Истец",
            "Name": "Компания Галфис Оверсиз Лимитед",
            "Address": "127055, ул. Бутырский вал д. 68/70 стр. 4/5 Москва",
            "Inn": null,
            "Ogrn": null,
            "Okpo": null
          },
        ],
        "Defendants": [ // список произвольной длины
          {
            "Type": "Ответчик",
            "Name": "ООО \"КОМПАНИЯ \"ФИНАНССТРОЙИНВЕСТМЕНТ\"",
            "Address": "107113, Россия, Москва, Сокольническая пл., д. 4А",
            "Inn": "7717532844",
            "Ogrn": "1057747067883",
            "Okpo": null
          },
        ],
        "Third": [ // список произвольной длины
          {
            "Type": "Третье лицо",
            "Name": "Компания Демесне Инвестментс Лимитед",
            "Address": "115114, Дербеневская наб 11В Москва",
            "Inn": null,
            "Ogrn": null,
            "Okpo": null
          }
        ],
        "Others": [ // список произвольной длины
          {
            "Type": "Заинтересованные лица",
            "Name": "Гурняк Я. Ф.",
            "Address": "Данные скрыты",
            "Inn": null,
            "Ogrn": null,
            "Okpo": null
          },
        ]
      },
    },
}

Card/CaseDocuments
Сведения о документах по делу.
Предполагаю, мониторить необходимо только наличие документов, их даты и состояние.

Пример:

{
    "Documents": [ // список произвольной длины
      {
        "Id": "b634f834-7798-425f-bf02-ec71b2732fe0",
        "CaseId": "9da5fb46-e6a4-4b2f-94bc-0d966e2ffb53",
        "InstanceId": "7d07af56-22fd-4170-a485-88fad158a206",
        "Type": "Приложения",
        "ContentTypes": [
          "Приложение к заявлению о пересмотре судебного акта в порядке надзора"
        ],
        "PublishDate": null,
        "DisplayDate": "29.05.2014",
        "AppealDate": null,
        "ActualDate": "2014-05-29T16:36:55",
        "Judges": [ // список произвольной длины
          {
            "Name": "Бобылёв М. П.",
            "Role": "Судья-докладчик"
          }
        ],
        "Declarers": [ // список произвольной длины
          {
            "Organization": "Компания Башкорт АБ",
            "Address": "119017, ул. Большая Ордынка, д. 40, стр. 5, г. Москва, АБ \"Егоров, Пугинский, Афанасьев и партнеры\" (внимнию: А.С. Ванеева, Т.З. Абушахманова)",
            "Inn": null,
            "Ogrn": null,
            "Type": 0
          }
        ],
        "HearingDate": null,
        "HearingPlace": null,
        "FileName": "",
        "IsDeleted": false,
        "DelDate": null,
        "WithAttachment": false,
        "HasSignature": false,
      },
}

На текущий момент эти примеры данных адекватно обрисовывают количество доступной информации.
Полагаю, надо как можно сильнее сократить перечень сохраняемых в БД атрибутов, чтобы максимально упростить
разработку системы.
