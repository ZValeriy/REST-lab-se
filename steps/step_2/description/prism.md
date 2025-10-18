# Mock-сервер
## Задание на лабораторную работу
- Скопируйте полученную вами спецификацию из п.1 в директорию steps/step_2/execution
- Напишите docker-compose-файл для своего варианта реализации мок-сервера в той же директории
### Простой уровень сложности
- Измените спецификацию, добавив статическое мокирование с помощью Prism
### Продвинутый 
- Измените спецификацию, добавив динамическое мокирование с помощью Prism
## Теория
### Зачем нужно мокирование
Нередко во время разработки новых программных компонентов или изменения существующих интеграций команды договариваются о новом контракте заранее, а саму доработку проводят в разное время по своим планам. Чтобы не тормозить тестирование и вывод в прод части функционала одной из команд, другая команда может предоставить мок‑сервер, который будет отвечать на запросы так, будто функциональность уже реализована. Это позволит протестировать задачу и вывести её, не дожидаясь реализации сервера. Практика API First отлично подходит для такого взаимодействия.
### Как сделать mock-сервер
Существует множество способов создать свой собственный mock-сервер, который будет имитировать работу реального сервиса и отвечать на запросы:
- написать самостоятельно
- использовать Postman
- использовать open source (и не только) решения
В ходе этой лабораторной работы мы будем использовать [Prism](https://docs.stoplight.io/docs/prism/674b27b261c3c-prism-overview). Этот мок-сервер позволяет при запуске приложения использовать описанную спецификацию openAPI, чтобы сгенерировать объекты. Prism – stateless mock, поэтому протестировать цепочки запросов не получится. Если необходимо такое поведение, то можно выбрать Postman/Karate/WireMock/MockServer/Hoverfly/Beeceptor. 
### Что нужно, чтобы Prism заработал
Чтобы поднять собственный mock-сервер с помощью Prism, нужно выполнить следующие действия:
- Написать спецификацию на методы в нотации openAPI
- Описать примеры (examples) для вызова в спецификации
- Описать docker-compose файл для конфигурации проекта
- Запустить mock-сервер
Если описано несколько примеров, то их можно выбрать по имени, использовав заголовок Prefer в запросе с передачей необходимого имени.
### Статическая генерация
Статическая генерация работает так, как указано выше. Prism берёт реальные примеры, прописанные вручную. Если примеров нет, то мок-сервер найдёт схему объекта, а дальше на её основе составить тело ответа по следующим правилам.
- Если свойство имеет значение по умолчанию, то оно вернет указанное значение.
- Если свойство имеет значение примера, то оно вернет первый элемент в массиве.
- Если свойство не имеет ни примера, ни значения по умолчанию и является нулевым, оно вернет null.
- Если свойство не имеет ни примера, ни значения по умолчанию и не является нулевым, но имеет указанный формат, то оно вернет значимое статическое значение в соответствии с форматом.
- Если свойство не имеет ни примера, ни значения по умолчанию, не является нулевым и не имеет указанного формата, то оно вернет «строка» в случае строки и 0 в случае числа. 

Мок-сервер можно запустить с флагом --ignore-examples. В этом случае Prism будет считать, что примеров нигде нет, и использует вторую часть алгоритма.
### Динамическая генерация
В динамическом режиме ответы будут больше похожи на реальные данные, так как мы сможем использовать генерацию на лету с помощью Faker.
Для этого мы должны запустить призм-сервер с флагом -d и изменить спецификацию, добавив к описанию схемы свойство x-faker со значением, равным методу в библиотеке генерации данных. Доступные методы можно найти по [ссылке](https://v6.fakerjs.dev/api/address.html)
Например, добавим динамическую генерацию для телефона клиента:
``` yaml
Client:
    type: object
    required:
    - id
    - login
    - status
    - created_at
    properties:
    id:
        description: "Идентификатор пользователя во внутренней системе"
        type: integer
        minimum: 0
        example: 1233998
    login:
        description: "Логин клиента, с которым он зарегистрировался на сайте"
        type: string
        example: Ivanov93
    status:
        type: string
        enum: [new, heavy, light]
        description: "Статус личного кабинета пользователя"
    created_at:
        type: string
        format: date
        description: "Дата регистрации пользователя"
    phone_number:
        type: string 
        pattern: '^\\+7\\d{10}$'
        example: "+79161234567"
        x-faker: phone.phoneNumber
        description: "Номер телефона в формате +7XXXXXXXXXX"
```
Можно контролировать генерацию, используя переменные из библиотеки. Например, сделать вот так для числа. В этом случае сгенерируется либо 10, либо 11:
```yaml
x-faker:
  datatype.number:
    min: 10
    max: 11
```
Можно описать базовые настройки генерации в корне спецификации API:
```yaml
x-json-schema-faker:
  locale: ru
  min-items: 2
  max-items: 10
  optionalsProbability: 0.5
  resolve-json-path: true
```
При вызове метода необходимо использовать заголовок Prefer со значением dynamic=true.

## Шаги
### Добавление разных вариантов ответа
#### Доработки спецификации
Возьмём файл [openAPI_example.yaml](../step_1/description/openAPI_example.yaml) и доработаем его, чтобы исследовать возможности мок‑сервера.
Добавим несколько примеров для получения информации о клиенте. В схемах уже есть примеры, поэтому добавим пример в описание самого метода GET /clients/{client_id}. Для этого примеры поместим на одном уровне со схемой. Скопируем его в директорию этого шага и изменим.
``` yaml
schema: 
    $ref: '#/components/schemas/ClientExtended'
examples:
    basicClient:
        summary: Basic client example
        value:
        id: "c12345"
        name: "Иван Петров"
        email: "ivan.petrov@example.com"
        phone: "+7-900-123-45-67"
        status: "active"
        registrationDate: "2023-11-15"
        loyalty:
            tier: "standard"
            points: 120
            cashbackRate: 0.03
        preferences:
            notifications: true
            preferredChannel: "email"
    vipClient:
        summary: VIP client example
        value:
        id: "c98765"
        name: "Ольга Смирнова"
        email: "olga.smirnova@example.com"
        phone: "+7-916-555-22-33"
        status: "vip"
        registrationDate: "2020-02-10"
        loyalty:
            tier: "gold"
            points: 8450
            cashbackRate: 0.1
        preferences:
            notifications: true
            preferredChannel: "personal_manager"
            vipSupport: true
```
#### Запуск mock-сервера
- В консоли напишите docker-compose up -d --build
- Выполните в консоли команды (или используйте Postman/Insomnia), убедитесь, что вернулись разные объекты
```bash
curl -u log:pass http://localhost:4010/clients/12345
```
```bash
curl -u log:pass http://localhost:4010/clients/12345 -H "Prefer: example=basicClient"
```
```bash
curl -u log:pass http://localhost:4010/clients/12345 -H "Prefer: example=vipClient"
```
- Можете проверить и остальные методы

### Добавление динамической генерации
#### Доработки спецификации
Продолжим работать в том же файле. На уровне description 200-го ответа добавим генерацию данных:
```yaml
    Client:
      type: object
      required:
        - id
        - login
        - status
        - created_at
      properties:
        id:
          description: "Идентификатор пользователя во внутренней системе"
          type: integer
          minimum: 1
          maximum: 9999999
          example: 1233998
          x-faker: number.int
        login:
          description: "Логин клиента, с которым он зарегистрировался на сайте"
          type: string
          minLength: 5
          maxLength: 20
          example: Ivanov93
          x-faker: internet.userName
        status:
          type: string
          enum: [new, heavy, light]
          description: "Статус личного кабинета пользователя"
          x-faker:
            random_element:
              elements: ["new", "heavy", "light"]
        created_at:
          type: string
          format: date
          description: "Дата регистрации пользователя"
          example: "2023-05-17"
          x-faker: date.past
        phone_number:
          type: string
          pattern: '^\\+7\\d{10}$'
          example: "+79161234567"
          description: "Номер телефона в формате +7XXXXXXXXXX"
          x-faker: 
            phone.phoneNumber:
              - '+79#########'
    ClientExtended:
      allOf:
      - $ref: '#/components/schemas/Client'
      - type: object
        properties:
          updated_at:
            type: string
            format: date-time
            description: "Дата последнего обновления профиля"
            example: "2023-10-01T16:00:00Z"
            x-faker: date.recent
          full_name:
            type: string
            description: "ФИО клиента"
            example: "Иванов Иван Иванович"
            x-faker: name.findName
          birth_date:
            type: string
            format: date
            description: "Дата рождения"
            example: "1993-05-17"
            x-faker: date_of_birth
          gender:
            type: string
            enum: [male, female, other]
            example: "male"
            description: "Пол клиента"
            x-faker:
              random_element:
                elements: ["male", "female"]
          loyalty_level:
            type: string
            enum: [bronze, silver, gold, platinum]
            description: "Уровень лояльности"
            example: "silver"
            x-faker:
              random_element:
                elements: ["bronze", "silver", "gold", "platinum"]
          last_login_at:
            type: string
            format: date-time
            example: "2023-10-01T18:00:00Z"
            description: "Дата последнего входа"
            x-faker: date.recent
          preferences:
            type: object
            description: "Настройки клиента"
            properties:
              language:
                type: string
                enum: [ru, en]
                example: "ru"
                x-faker:
                  random_element:
                    elements: ["ru", "en"]
              notifications:
                type: boolean
                example: true
                x-faker: datatype.boolean
          tags:
            type: array
            items:
              type: string
              x-faker: internet.color
            description: "Метки клиента"
            example: ["test_group", "vip"]
```
Еще в корне спецификации укажем общие настройки:
```yaml
x-json-schema-faker:
  locale: ru
  min-items: 2
  max-items: 10
  optionalsProbability: 0.5
```
Далее перезапустим docker-compose проект, используя команду
```bash
docker-compose up -d
```
- Выполните в консоли команды (или используйте Postman/Insomnia), убедитесь, что возвращаются разные объекты
```bash
curl -u log:pass http://localhost:4010/clients/123 -H 'Prefer: dynamic=true'
``` 
```bash
curl -u log:pass http://localhost:4010/clients/144 -H 'Prefer: dynamic=true'
``` 
#### AI-помощник
Вы можете попросить любую LLM-модель сгенерировать различные примеры под ваш случай, в том числе придумав корнер‑кейсы для проверок. В [файле](./prompt.txt) приведён пример промпта для генерации примеров. Попробуйте его в любой LLM‑модели и проверьте результат.

## Контрольные вопросы
- Чем отличаются статическое и динамическое мокирование в Prism?
- Для чего используется заголовок `Prefer` и какие значения он принимает?
- Почему Prism считается stateless и к чему это приводит при тестировании?
- Какие альтернативные инструменты подходят для stateful‑мокирования?
- Где в спецификации OpenAPI размещают `examples` и где — `x-faker`?
